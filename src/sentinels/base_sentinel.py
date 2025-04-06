import json
import logging
from src.config import get_settings
from src.constants import RequestStatus
from src.state_manager import StateManager
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseSentinel(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        self.settings = get_settings()
        self.state = StateManager()

    async def _initialize_status(self, request_id: str):
        """Initialize sentinel status for this request"""
        await self.state.set_sentinel_status(
            request_id=request_id,
            sentinel_name=self.name,
            status=RequestStatus.PENDING
        )

    async def _process_request(self, data: dict):
        """Process incoming request"""
        request_id = data.get("request_id")
        await self._initialize_status(request_id)

        try:
            request_data = data.get("data")
            result = await self.analyze(request_data)
            status = RequestStatus.COMPLETED
            logger.info(f"✅ Sentinel {self.name} completed analysis for request {request_id}")
        except Exception as e:
            result = {"error": str(e)}
            status = RequestStatus.ERROR
            logger.error(f"❌ Sentinel {self.name} failed analysis for request {request_id}: {e}")

        await self.state.set_sentinel_status(
            request_id=request_id,
            sentinel_name=self.name,
            status=status,
            result=result
        )

    async def listen(self):
        """Listen for incoming requests"""
        channel = self.settings.REDIS_CHANNELS.SENTINELS_INPUT.value
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
    
    @abstractmethod
    async def analyze(self, data: dict) -> dict:
        """Each sentinel must implement its own analysis logic"""
        pass