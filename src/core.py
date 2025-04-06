import logging
import asyncio
import time
import uuid

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

    async def _dispatch_sentinels_request(self, request_id: str):
        """Initialize request state and notify sentinels"""
        # Load sentinels if not already loaded
        if not self.expected_sentinels:
            self.expected_sentinels = await self.state.get_active_sentinels()

        if not self.expected_sentinels:
            raise ValueError("No sentinels found")

        # Notify sentinels via PubSub
        await self.state.publish_message(
            self.settings.REDIS_CHANNELS.SENTINELS_INPUT,
            {
                "request_id": request_id
            }
        )
        logger.info(f"Request {request_id} dispatched to sentinels")
    
    async def _dispatch_agent_request(self, request_id: str):
        await self.state.publish_message(
            self.settings.REDIS_CHANNELS.AGENT_INPUT,
            {
                "request_id": request_id
            }
        )

    async def _wait_for_sentinels_analysis(self, request_id: str) -> dict:
        """Wait for analysis completion and return results"""
        timeout = self.settings.ANALYSIS_EXPIRATION_TIME
        start_time = time.time()
        
        while True:
            # Check status of each sentinel
            sentinel_statuses = await self.state.get_sentinel_statuses(request_id)
            completed_sentinels = set(sentinel for sentinel, status in sentinel_statuses.items() 
                                   if status["status"] == RequestStatus.COMPLETED)
            
            # Check if all sentinels have completed
            if completed_sentinels and completed_sentinels >= self.expected_sentinels:
                logger.info(f"✅ All sentinels completed analysis for request {request_id}")
                return sentinel_statuses
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Request {request_id} timed out")
            
            await asyncio.sleep(0.1)

    async def _wait_for_agent_decision(self, request_id: str) -> dict:
        """Wait for agent decision and return results"""
        timeout = self.settings.ANALYSIS_EXPIRATION_TIME
        start_time = time.time()
        
        while True:
            # Check current request state
            agent_status = await self.state.get_agent_status(request_id)
            
            if agent_status and agent_status.get("status") == RequestStatus.COMPLETED:
                logger.info(f"✅ Agent decision received for request {request_id}")
                return agent_status
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Request {request_id} timed out waiting for agent decision")
            
            await asyncio.sleep(0.1)

    async def analyze_transaction(self, data: dict) -> dict:
        """Process request and wait for results"""
        
        request_id = await self.state.initialize_request(data)
        
        await self._dispatch_sentinels_request(request_id)

        sentinel_results = await self._wait_for_sentinels_analysis(request_id)
        logger.info(f"Sentinel results: {sentinel_results}")

        # Dispatch request to agent with sentinel results
        await self._dispatch_agent_request(request_id)

        logger.info(f"Waiting for agent decision for request {request_id}")
        agent_decision = await self._wait_for_agent_decision(request_id)
        
        logger.info(f"Agent decision received for request {request_id}")
        # Update final request status
        await self.state.set_request_status(
            request_id=request_id,
            status=RequestStatus.COMPLETED
        )

        return {
            "request_id": request_id,
            "approved": agent_decision.get("result", {}).get("approved", False)
        }

core = CoreService()