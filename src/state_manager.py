import json
import logging
import time
import uuid

from src.config import get_settings
from typing import Any, Dict, Optional, List, Set
from redis.asyncio import Redis
from src.constants import RequestStatus

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

    async def initialize_request(self, data: dict) -> None:
        """Initialize a new request with the unified structure"""
        if not self._redis:
            await self.init()
        
        request_id = str(uuid.uuid4())
        # Create base structure
        request_data = {
            "request_id": request_id,
            "chainId": data.get("chainId", ""),
            "from_address": data.get("from_address", ""),
            "to_address": data.get("to_address", ""),
            "data": data.get("data", ""),
            "value": data.get("value", "0"),
            "reason": data.get("reason", ""),
            "validations": json.dumps([]),  # Serialize list
            "created_at": str(time.time()),
            "status": RequestStatus.PENDING
        }
        
        # Store in Redis as hash
        await self._redis.hset(f"request:{request_id}", mapping=request_data)
        await self._redis.expire(f"request:{request_id}", get_settings().ANALYSIS_EXPIRATION_TIME)
        
        return request_id

    async def set_request(self, request_id: str, request_data: dict) -> None:
        """Store a new request in Redis"""
        if not self._redis:
            await self.init()
        
        # Convert dict to flat key-value pairs for hash
        for key, value in request_data.items():
            # Serialize complex values (lists, dicts) to JSON strings
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self._redis.hset(f"request:{request_id}", key, value)

    async def get_request(self, request_id: str) -> Optional[dict]:
        """Retrieve a request from Redis"""
        if not self._redis:
            await self.init()
        
        # Get all fields from hash
        data = await self._redis.hgetall(f"request:{request_id}")
        if not data:
            return None
        
        # Convert back to dict and deserialize JSON values
        result = {}
        for key, value in data.items():
            try:
                # Attempt to deserialize JSON values
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                # If not JSON, keep original value
                result[key] = value
        
        return result

    async def set_sentinel_status(self, request_id: str, sentinel_name: str, status: str, result: Any = None) -> None:
        """Update a sentinel's status in the unified request record"""
        if not self._redis:
            await self.init()
        
        # Get current validations
        validations_json = await self._redis.hget(f"request:{request_id}", "validations")
        validations = json.loads(validations_json) if validations_json else []
        
        # Ensure result is a dictionary if provided
        if result is not None:
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            elif not isinstance(result, dict):
                result = {"result": result}
        
        # Update or add sentinel status
        sentinel_found = False
        for validation in validations:
            if validation.get("name") == sentinel_name:
                validation["status"] = status
                if result is not None:
                    validation["result"] = result
                sentinel_found = True
                break
        
        if not sentinel_found:
            validations.append({
                "name": sentinel_name,
                "status": status,
                **({"result": result} if result is not None else {})
            })
        
        # Update validations in Redis
        await self._redis.hset(
            f"request:{request_id}", 
            "validations", 
            json.dumps(validations)
        )

    async def get_sentinel_statuses(self, request_id: str) -> Dict:
        """Get all sentinel statuses for a request from the unified structure"""
        request_data = await self.get_request(request_id)
        if not request_data:
            return {}
        
        sentinel_statuses = {}
        for validation in request_data.get("validations", []):
            if validation.get("name") != "agent":  # Exclude agent from sentinel results
                sentinel_statuses[validation.get("name")] = {
                    "status": validation.get("status"),
                    "result": validation.get("result", {})
                }
        
        return sentinel_statuses

    async def set_request_status(self, request_id: str, status: str, data: Any = None) -> None:
        """Update the overall request status and optionally add data"""
        request_data = await self.get_request(request_id)
        
        if not request_data:
            if data:
                # Initialize new request
                request_data = await self.initialize_request(request_id, data)
            else:
                logger.error(f"Request {request_id} not found and no data provided to create it")
                return
        
        # Update status and timestamp
        await self._redis.hset(f"request:{request_id}", mapping={
            "status": status,
            "updated_at": str(time.time())
        })
        
        # If any additional data is provided, update it
        if data and isinstance(data, dict):
            update_data = {}
            for key, value in data.items():
                if key not in ["validations", "request_id", "created_at", "updated_at"]:
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    update_data[key] = value
            
            if update_data:
                await self._redis.hset(f"request:{request_id}", mapping=update_data)
        
        # Set expiration
        await self._redis.expire(f"request:{request_id}", get_settings().ANALYSIS_EXPIRATION_TIME)

    async def set_agent_status(self, request_id: str, status: str, result: Any = None) -> None:
        """Set agent status in the unified request record"""
        await self.set_sentinel_status(request_id, "agent", status, result)

    async def get_agent_status(self, request_id: str) -> Optional[Dict]:
        """Get agent status from the unified request record"""
        request_data = await self.get_request(request_id)
        if not request_data:
            return None
        
        for validation in request_data.get("validations", []):
            if validation.get("name") == "agent":
                return {
                    "status": validation.get("status"),
                    "result": validation.get("result", {})
                }
        
        return None

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

    async def get_all_requests(self) -> List[str]:
        """Get all request IDs"""
        if not self._redis:
            await self.init()
        keys = await self._redis.keys("request:*")
        return [key.split(":")[1] for key in keys]

    async def get_request_details(self, request_id: str) -> Optional[dict]:
        """Get full request details - for backward compatibility"""
        return await self.get_request(request_id) 