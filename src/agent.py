import logging
from typing import Dict, Any
import asyncio
import json
import time
from src.state_manager import StateManager
from src.constants import TransactionStatus
from src.config import get_settings

logger = logging.getLogger(__name__)

class BAIbyAgent:
    def __init__(self):
        self.state = StateManager()
        self.settings = get_settings()
        self.name = "agent"  # Changed to match expected format in validations

    async def _initialize_status(self, transaction_id: str):
        """Initialize agent status for this transaction"""
        await self.state.set_agent_status(
            transaction_id=transaction_id,
            status=TransactionStatus.PENDING
        )

    async def _process_transaction(self, data: dict):
        """Process received messages from channel"""
        transaction_id = data.get("transaction_id")
        
        if not transaction_id:
            logger.error(f"{self.name} received message without transaction_id")
            return
            
        await self._initialize_status(transaction_id)
        
        try:
            logger.info(f"🤖 {self.name} processing transaction {transaction_id}")
            await self.analyze(data)
            
        except Exception as e:
            logger.error(f"Error processing message in {self.name}: {e}")
            # Update status to error
            await self.state.set_sentinel_status(
                transaction_id=transaction_id,
                sentinel_name=self.name,
                status=TransactionStatus.ERROR,
                result={"error": str(e)}
            )

    async def listen(self):
        """Listen for agent channel events"""
        channel = self.settings.REDIS_CHANNELS.AGENT_INPUT.value
        pubsub = await self.state.subscribe_to_channel(channel)
        
        try:
            async for message in pubsub.listen():
                logger.info(f"🤖 {self.name} received message: {message}")
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    await self._process_transaction(data)
        except Exception as e:
            logger.error(f"Error in {self.name} listener: {e}")
            raise

    async def analyze(self, data: Dict[str, Any]):
        """Analyze sentinel results and make final decision"""
        
        transaction_id = data["transaction_id"]
        
        # Get sentinel results from the provided data or fetch them
        sentinel_results = data.get("sentinel_results", {})
        if not sentinel_results:
            sentinel_results = await self.state.get_sentinel_statuses(transaction_id)

        try:
            high_risk = False
            warnings = []

            for sentinel_name, result in sentinel_results.items():
                result_data = result.get("result", {})
                if result_data.get("risk_level") == "high":
                    high_risk = True
                    warnings.append(f"High risk detected by {sentinel_name}: {result_data.get('reason')}")
                elif result_data.get("risk_level") == "medium":
                    warnings.append(f"Warning from {sentinel_name}: {result_data.get('reason')}")

            result = {
                "status": "success",
                "message": "Analysis completed successfully",
                "approved": not high_risk,
                "risk_level": "high" if high_risk else "low",
                "warnings": warnings,
                "timestamp": time.time()
            }

            status = TransactionStatus.COMPLETED
            logger.info(f"✅ Agent completed analysis for transaction {transaction_id}")
        except Exception as e:
            result = {"error": str(e)}
            status = TransactionStatus.ERROR
            logger.error(f"❌ Agent failed analysis for transaction {transaction_id}: {e}")

        await self.state.set_agent_status(
            transaction_id=transaction_id,
            status=status,
            result=result
        )
