import json
import logging
import asyncio
import time
import aioredis

from typing import Dict, Set
from src.config import get_settings
from enum import Enum

logger = logging.getLogger(__name__)

class RequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

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
        self.redis = None
        self.expected_sentinels = {"malicious-address-sentinel"}

    async def connect(self):
        """Connect to Redis"""
        if not self.redis:
            self.redis = await aioredis.from_url(self.settings.REDIS_URL)
            logger.info("Connected to Redis")

    async def analyze_transaction(self, data: dict) -> dict:
        """Process request and wait for results"""
        request_id = data["request_id"]
        await self._dispatch_sentinels_request(data)
        
        # Wait for completion
        timeout = self.settings.ANALYSIS_EXPIRATION_TIME
        start_time = time.time()
        
        while True:
            request_key = f"request:{request_id}"
            request_data = await self.redis.hgetall(request_key)
            
            if request_data["status"] == RequestStatus.COMPLETED:
                return json.loads(request_data["results"])
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Request {request_id} timed out")
            
            await asyncio.sleep(0.1)
            
    async def handle_sentinel_response(self, message: dict):
        """Update request state with sentinel results"""
        request_id = message["request_id"]
        sentinel_name = message["sentinel"]
        analysis = message["analysis"]

        request_key = f"request:{request_id}"
        
        # Update request state atomically
        async with self.redis.pipeline(transaction=True) as pipe:
            # Get current state
            request_data = await pipe.hgetall(request_key)
            
            pending_sentinels = json.loads(request_data["pending_sentinels"])
            results = json.loads(request_data["results"])
            
            # Update state
            pending_sentinels.remove(sentinel_name)
            results[sentinel_name] = analysis
            
            # Store updated state
            await pipe.hset(request_key, mapping={
                "pending_sentinels": json.dumps(pending_sentinels),
                "results": json.dumps(results),
                "status": RequestStatus.COMPLETED if not pending_sentinels else RequestStatus.PROCESSING
            })

    async def _dispatch_sentinels_request(self, data: dict):
        """Initialize request state and notify sentinels"""
        request_id = data["request_id"]
        
        # Initialize base request state
        request_key = f"request:{request_id}"
        await self.redis.hset(request_key, mapping={
            "status": RequestStatus.PENDING,
            "data": json.dumps(data),
            "expected_sentinels": json.dumps(list(self.expected_sentinels)),  # Solo para referencia
            "created_at": str(time.time())
        })
        await self.redis.expire(request_key, self.settings.ANALYSIS_EXPIRATION_TIME)

        # Notify sentinels via PubSub
        await self.redis.publish(
            self.settings.REDIS_CHANNELS.SENTINELS_INPUT,
            json.dumps({"request_id": request_id, "data": data})
        )
        logger.info(f"Request {request_id} dispatched to sentinels")

core = CoreService()