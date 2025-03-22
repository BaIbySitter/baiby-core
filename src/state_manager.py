import json
import logging
import time
from src.config import get_settings
from typing import Any, Dict, Optional
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class StateManager:
    _instance = None
    _redis: Optional[Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init(self):
        """Initialize state manager"""
        if not self._redis:
            settings = get_settings()
            self._redis = Redis.from_url(
                url=settings.REDIS_URL,
                decode_responses=True
            )
            logger.info("State manager initialized")

    async def close(self):
        """Close connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("State manager closed")

    async def set_sentinel_status(self, request_id: str, sentinel_name: str, status: str, result: Any = None):
        """Set status and result for a specific sentinel"""
        key = f"sentinel_status:{request_id}"
        value = {
            "status": status,
            "result": result
        }
        await self._redis.hset(key, sentinel_name, json.dumps(value))
        await self._redis.expire(key, get_settings().ANALYSIS_EXPIRATION_TIME)

    async def get_sentinel_statuses(self, request_id: str) -> Dict:
        """Get all sentinel statuses for a request"""
        key = f"sentinel_status:{request_id}"
        statuses = await self._redis.hgetall(key)
        return {k: json.loads(v) for k, v in statuses.items()}

    async def set_request_status(self, request_id: str, status: str, data: Any = None):
        """Set status and data for a request"""
        key = f"request:{request_id}"
        
        # Check if request exists
        exists = await self._redis.exists(key)
        
        if not exists:
            # New request - set all initial fields
            mapping = {
                "status": status,
                "data": json.dumps(data) if data else None,
                "created_at": str(time.time())
            }
        else:
            # Existing request - update status and set updated_at
            mapping = {
                "status": status,
                "updated_at": str(time.time())
            }
            
        await self._redis.hset(key, mapping=mapping)
        await self._redis.expire(key, get_settings().ANALYSIS_EXPIRATION_TIME)

    async def subscribe_to_channel(self, channel: str):
        """Create and return a pubsub subscription"""
        if not self._redis:
            await self.init()
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def publish_message(self, channel: str, message: dict):
        """Publish message to Redis channel"""
        if not self._redis:
            await self.init()
        message_str = json.dumps(message)
        await self._redis.publish(channel, message_str)
        logger.debug(f"Published message to {channel}: {message_str}")

    async def set_active_sentinels(self, sentinel_names: set):
        """Store the set of active sentinels"""
        if not self._redis:
            await self.init()
        await self._redis.sadd("active_sentinels", *sentinel_names)

    async def get_active_sentinels(self) -> set:
        """Get the set of active sentinels"""
        if not self._redis:
            await self.init()
        members = await self._redis.smembers("active_sentinels")
        return set(members) 