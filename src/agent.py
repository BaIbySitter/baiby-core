import logging
from typing import Dict, Any
import asyncio
import json
from src.state_manager import StateManager
from src.constants import RequestStatus, RedisChannels
from src.config import get_settings

logger = logging.getLogger(__name__)

class BAIbyAgent:
    def __init__(self):
        self.state = StateManager()
        self.settings = get_settings()
        self.name = "baiby-agent"

    async def _initialize_status(self, request_id: str):
        """Initialize sentinel status for this request"""
        await self.state.set_sentinel_status(
            request_id=request_id,
            sentinel_name=self.name,
            status=RequestStatus.PENDING
        )

    async def _process_request(self, data: dict):
        """Process received messages from channel"""
        request_id = data.get("request_id")
        await self._initialize_status(request_id)
        
        try:
            if not request_id:
                logger.error(f"{self.name} received message without request_id")
                return
                
            logger.info(f"🤖 {self.name} processing request {request_id}")
            await self.analyze(data)
            
        except Exception as e:
            logger.error(f"Error processing message in {self.name}: {e}")

    async def listen(self):
        """Listen for agent channel events"""
        channel = self.settings.REDIS_CHANNELS.AGENT_INPUT.value
        pubsub = await self.state.subscribe_to_channel(channel)
        
        try:
            async for message in pubsub.listen():
                logger.info(f"🤖 {self.name} received message: {message}")
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    await self._process_request(data)
        except Exception as e:
            logger.error(f"Error in {self.name} listener: {e}")
            raise

    async def analyze(self, data: Dict[str, Any]):
        """Analyze sentinel results and make final decision"""
        
        request_id = data["request_id"]
        
        logger.info(f"🤖 {self.name} analyzing request {request_id}")
        current_state = await self.state.get_request_details(request_id)
        if not current_state:
            logger.error(f"Request {request_id} not found in state")
            return

        try:
            high_risk = False
            warnings = []

            for sentinel_name, result in current_state.items():
                if result.get("risk_level") == "high":
                    high_risk = True
                    warnings.append(f"High risk detected by {sentinel_name}: {result.get('reason')}")
                elif result.get("risk_level") == "medium":
                    warnings.append(f"Warning from {sentinel_name}: {result.get('reason')}")

            result = {
                "approved": not high_risk,
                "risk_level": "high" if high_risk else "low",
                "warnings": warnings,
                "timestamp": asyncio.get_event_loop().time()
            }

            status = RequestStatus.COMPLETED
            logger.info(f"✅ bAIby agent completed analysis for request {request_id}")
        except Exception as e:
            result = {"error": str(e)}
            status = RequestStatus.ERROR
            logger.error(f"❌ bAIby agent failed analysis for request {request_id}: {e}")

        await self.state.set_agent_status(
            request_id=request_id,
            status=status,
            result=result
        )
