import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from supabase import create_client
from src.config import get_settings
from src.constants import TransactionStatus
from src.state_manager import StateManager

logger = logging.getLogger(__name__)

class PersistenceService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized') or not self.initialized:
            self.settings = get_settings()
            self.state = StateManager()
            self.supabase = None
            self.initialized = True
    
    async def init_supabase(self):
        """Initialize Supabase client if not already initialized"""
        if not self.supabase and self.settings.SUPABASE_URL and self.settings.SUPABASE_KEY:
            self.supabase = create_client(
                self.settings.SUPABASE_URL,
                self.settings.SUPABASE_KEY
            )
            logger.info("Supabase client initialized")
            return True
        return self.supabase is not None
    
    async def persist_transaction(self, transaction_id: str):
        """Persist transaction data to Supabase"""
        try:
            supabase_available = await self.init_supabase()
            if not supabase_available:
                logger.warning("Supabase client not initialized, skipping persistence")
                return False
                
            # Get all transaction data
            transaction_data = await self.state.get_transaction(transaction_id)
            if not transaction_data:
                logger.error(f"❌ Transaction {transaction_id} not found for persistence")
                return False
            
            # Prepare the data in the required format for Supabase
            supabase_record = {
                "transaction_id": transaction_id,
                "from_address": transaction_data.get("from_address", ""),
                "data": transaction_data  # Store the entire object as JSON
            }
                    
            # Insert into Supabase
            self.supabase.table('transactions').insert(supabase_record).execute()
            logger.info(f"✅ Transaction {transaction_id} persisted in Supabase")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error persisting transaction {transaction_id} in Supabase: {e}")
            return False
    
    async def get_transactions_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
        """
        Get summarized data from Redis and Supabase for the dashboard
        
        Returns:
            Tuple with (active_transactions, completed_transactions, total_count)
            Each transaction only includes the essential fields for the dashboard
        """
        # Initialize the lists for the transactions
        all_transactions = []
        
        # Get active transactions from Redis
        redis_transaction_ids = await self.state.get_all_transactions()
        for transaction_id in redis_transaction_ids:
            transaction = await self.state.get_transaction(transaction_id)
            if transaction:
                # Convert timestamps to ISO strings
                if isinstance(transaction.get('created_at'), (int, float)):
                    transaction['created_at'] = datetime.fromtimestamp(float(transaction['created_at'])).isoformat()
                
                # Extract only the necessary fields for the dashboard
                summary = {
                    'transaction_id': transaction.get('transaction_id'),
                    'from_address': transaction.get('from_address', ''),
                    'created_at': transaction.get('created_at'),
                    'status': transaction.get('status')
                }
                all_transactions.append(summary)
        
        # Get historical transactions from Supabase
        supabase_available = await self.init_supabase()
        if supabase_available:
            try:
                # Get records from Supabase - limited to the last 100 for performance
                response = self.supabase.table('transactions').select('transaction_id, from_address, created_at, data->status').order('created_at', desc=True).limit(100).execute()
                
                if response.data:
                    for record in response.data:
                        # Build the summary directly from the selected fields
                        transaction_id = record.get('transaction_id')
                        
                        # Asegurarse que no procesamos duplicados que ya existen en Redis
                        if transaction_id not in redis_transaction_ids:
                            summary = {
                                'transaction_id': transaction_id,
                                'from_address': record.get('from_address', ''),
                                'created_at': record.get('created_at'),
                                'status': record.get('status')
                            }
                            all_transactions.append(summary)
            except Exception as e:
                logger.warning(f"Error retrieving data from Supabase: {e}")
        
        # Split into active and completed
        active = [t for t in all_transactions if t.get('status') != TransactionStatus.COMPLETED]
        completed = [t for t in all_transactions if t.get('status') == TransactionStatus.COMPLETED]
        
        # Limit results for better performance
        active = active[:100]  # show the 100 most recent ones
        completed = completed[:100]  # show the 100 most recent ones
        
        return active, completed, len(all_transactions)
    
    async def get_transaction_details(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the details of a transaction, first from Redis and then from Supabase if necessary
        
        Args:
            transaction_id: ID of the transaction to search for
            
        Returns:
            Dictionary with the transaction details or None if not found
        """
        # First try to get from Redis (active transactions)
        transaction = await self.state.get_transaction(transaction_id)
        
        # If not in Redis, search in Supabase
        if not transaction:
            supabase_available = await self.init_supabase()
            if supabase_available:
                try:
                    response = self.supabase.table('transactions')\
                        .select('data')\
                        .eq('transaction_id', transaction_id)\
                        .execute()
                    
                    if response.data and len(response.data) > 0:
                        transaction = response.data[0].get('data', {})
                except Exception as e:
                    logger.error(f"Error retrieving transaction from Supabase: {e}")
        
        if not transaction:
            return None
            
        # Convert timestamps to ISO strings if necessary
        if isinstance(transaction.get('created_at'), (int, float)):
            transaction['created_at'] = datetime.fromtimestamp(float(transaction['created_at'])).isoformat()
        if isinstance(transaction.get('updated_at'), (int, float)) and transaction.get('updated_at'):
            transaction['updated_at'] = datetime.fromtimestamp(float(transaction['updated_at'])).isoformat()
            
        return transaction
    
    async def listen(self):
        """Listen for persistence messages on Redis channel"""
        channel = self.settings.REDIS_CHANNELS.PERSISTENCE.value
        pubsub = await self.state.subscribe_to_channel(channel)
        
        logger.info(f"🔄 Persistence service listening on channel: {channel}")
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    logger.info(f"📥 Received persistence message: {data}")
                    
                    if data.get('type') == 'persist_transaction':
                        transaction_id = data.get('transaction_id')
                        if transaction_id:
                            await self.persist_transaction(transaction_id)
        except Exception as e:
            logger.error(f"❌ Error in persistence service listener: {e}")
            # Reconnect after error
            await asyncio.sleep(5)
            await self.listen()

# Singleton to access the persistence service
def get_persistence_service() -> PersistenceService:
    return PersistenceService()

async def run_persistence_service():
    """Run the persistence service"""
    service = get_persistence_service()
    await service.listen()

if __name__ == "__main__":
    # This allows running the service standalone
    import asyncio
    asyncio.run(run_persistence_service())