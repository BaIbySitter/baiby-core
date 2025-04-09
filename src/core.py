import logging
import asyncio
import time

from src.config import get_settings
from src.constants import TransactionStatus
from src.state_manager import StateManager

logger = logging.getLogger(__name__)

class CoreService:
    """
    Core service that orchestrates:
    - Receives transactions from API/RPC
    - Coordinates sentinel analysis
    - Communicates with baby-agent
    - Aggregates responses
    - Returns final results
    """
    def __init__(self):
        self.settings = get_settings()
        self.state = StateManager()
        self.expected_sentinels = set()

    async def _dispatch_transaction_to_sentinels(self, transaction_id: str):
        """Initialize transaction state and notify sentinels"""
        # Load sentinels if not already loaded
        if not self.expected_sentinels:
            self.expected_sentinels = await self.state.get_active_sentinels()

        if not self.expected_sentinels:
            raise ValueError("No sentinels found")

        # Notify sentinels via PubSub
        await self.state.publish_message(
            self.settings.REDIS_CHANNELS.SENTINELS_INPUT.value,
            {
                "transaction_id": transaction_id
            }
        )
        logger.info(f"Transaction {transaction_id} dispatched to sentinels")
    
    async def _dispatch_transaction_to_agent(self, transaction_id: str):
        await self.state.publish_message(
            self.settings.REDIS_CHANNELS.AGENT_INPUT.value,
            {
                "transaction_id": transaction_id
            }
        )

    async def _wait_for_sentinels_analysis(self, transaction_id: str) -> dict:
        """Wait for analysis completion and return results"""
        timeout = self.settings.ANALYSIS_EXPIRATION_TIME
        start_time = time.time()
        
        while True:
            # Check status of each sentinel
            sentinel_statuses = await self.state.get_sentinel_statuses(transaction_id)
            completed_sentinels = set(sentinel for sentinel, status in sentinel_statuses.items() 
                                   if status["status"] == TransactionStatus.COMPLETED)
            
            # Check if all sentinels have completed
            if completed_sentinels and completed_sentinels >= self.expected_sentinels:
                logger.info(f"✅ All sentinels completed analysis for transaction {transaction_id}")
                return sentinel_statuses
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Transaction {transaction_id} timed out")
            
            await asyncio.sleep(0.1)

    async def _wait_for_agent_decision(self, transaction_id: str) -> dict:
        """Wait for agent decision and return results"""
        timeout = self.settings.ANALYSIS_EXPIRATION_TIME
        start_time = time.time()
        
        while True:
            # Check current transaction state
            agent_status = await self.state.get_agent_status(transaction_id)
            
            if agent_status and agent_status.get("status") == TransactionStatus.COMPLETED:
                logger.info(f"✅ Agent decision received for transaction {transaction_id}")
                return agent_status
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Transaction {transaction_id} timed out waiting for agent decision")
            
            await asyncio.sleep(0.1)

    async def analyze_transaction(self, data: dict) -> dict:
        """Process transaction and wait for results"""
        
        transaction_id = await self.state.initialize_transaction(data)

        await self._dispatch_transaction_to_sentinels(transaction_id)

        sentinel_results = await self._wait_for_sentinels_analysis(transaction_id)
        logger.info(f"Sentinel results: {sentinel_results}")

        # Dispatch transaction to agent with sentinel results
        await self._dispatch_transaction_to_agent(transaction_id)

        logger.info(f"Waiting for agent decision for transaction {transaction_id}")
        agent_decision = await self._wait_for_agent_decision(transaction_id)
        
        logger.info(f"Agent decision received for transaction {transaction_id}")
        # Update final transaction status
        await self.state.set_transaction_status(
            transaction_id=transaction_id,
            status=TransactionStatus.COMPLETED
        )

        transaction = await self.state.get_transaction(transaction_id)
        return transaction

core = CoreService()