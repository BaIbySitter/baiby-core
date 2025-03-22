import logging
import asyncio
import time

from src.config import get_settings
from src.constants import RequestStatus
from src.state_manager import StateManager

logger = logging.getLogger(__name__)

class CoreService:
    """
    Core service that orchestrates:
    - Receives requests from API/RPC
    - Coordinates sentinel analysis
    - Communicates with baby-agent
    - Aggregates responses
    - Returns final results
    """
    def __init__(self):
        self.settings = get_settings()
        self.state = StateManager()
        self.expected_sentinels = set()

    async def _dispatch_sentinels_request(self, data: dict):
        """Initialize request state and notify sentinels"""
        # Load sentinels if not already loaded
        if not self.expected_sentinels:
            self.expected_sentinels = await self.state.get_active_sentinels()
            
        request_id = data["request_id"]
        
        # Initialize base request state
        await self.state.set_request_status(
            request_id=request_id,
            status=RequestStatus.PENDING,
            data=data
        )

        # Notify sentinels via PubSub
        await self.state.publish_message(
            self.settings.REDIS_CHANNELS.SENTINELS_INPUT,
            {"request_id": request_id, "data": data}
        )
        logger.info(f"Request {request_id} dispatched to sentinels")

    async def _wait_for_sentinels_analysis(self, request_id: str, timeout: float) -> dict:
        """Wait for analysis completion and return results"""
        start_time = time.time()
        results = {}
        
        while True:
            # Check status of each sentinel
            sentinel_statuses = await self.state.get_sentinel_statuses(request_id)
            completed_sentinels = set()
            
            for sentinel, status in sentinel_statuses.items():
                if status["status"] == RequestStatus.COMPLETED:
                    completed_sentinels.add(sentinel)
                    results[sentinel] = status["result"]
            
            # Check if all sentinels have completed
            if completed_sentinels == self.expected_sentinels:
                await self.state.set_request_status(
                    request_id=request_id,
                    status=RequestStatus.COMPLETED
                )
                logger.info(f"✅ All sentinels completed analysis for request {request_id}")
                return results
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Request {request_id} timed out")
            
            await asyncio.sleep(0.1)

    async def analyze_transaction(self, data: dict) -> dict:
        """Process request and wait for results"""
        request_id = data["request_id"]
        await self._dispatch_sentinels_request(data)
        sentinel_results = await self._wait_for_sentinels_analysis(
            request_id, 
            self.settings.ANALYSIS_EXPIRATION_TIME
        )
        logger.info(f"Sentinel results: {sentinel_results}")

        return {
            "request_id": request_id,
            "warnings": [],
        }

core = CoreService()