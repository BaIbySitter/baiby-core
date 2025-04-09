import json
import logging
import time
import uuid
from supabase import Client
from src.config import get_settings
from typing import Any, Dict, Optional, List
from redis.asyncio import Redis
from src.constants import TransactionStatus

logger = logging.getLogger(__name__)

class StateManager:
    _instance = None
    _redis: Optional[Redis] = None
    _supabase: Optional[Client] = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init(self):
        """Initialize state manager"""
        if not self._redis:
            self.settings = get_settings()
            self._redis = Redis.from_url(
                url=self.settings.REDIS_URL,
                decode_responses=True
            )
            logger.info("State manager initialized")

    async def close(self):
        """Close connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("State manager closed")

    async def initialize_transaction(self, data: dict) -> None:
        """Initialize a new transaction with the unified structure"""
        if not self._redis:
            await self.init()
        
        transaction_id = str(uuid.uuid4())
        # Create base structure
        transaction_data = {
            "transaction_id": transaction_id,
            "chainId": data.get("chainId", ""),
            "from_address": data.get("from_address", ""),
            "to_address": data.get("to_address", ""),
            "data": data.get("data", ""),
            "value": data.get("value", "0"),
            "reason": data.get("reason", ""),
            "validations": json.dumps([]),  # Serialize list
            "created_at": str(time.time()),
            "status": TransactionStatus.PENDING
        }
        
        # Store in Redis as hash
        await self._redis.hset(f"transaction:{transaction_id}", mapping=transaction_data)
        await self._redis.expire(f"transaction:{transaction_id}", self.settings.ANALYSIS_EXPIRATION_TIME)
        
        return transaction_id

    async def set_transaction(self, transaction_id: str, transaction_data: dict) -> None:
        """Store a new transaction in Redis"""
        if not self._redis:
            await self.init()
        
        # Convert dict to flat key-value pairs for hash
        for key, value in transaction_data.items():
            # Serialize complex values (lists, dicts) to JSON strings
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self._redis.hset(f"transaction:{transaction_id}", key, value)

    async def get_transaction(self, transaction_id: str) -> Optional[dict]:
        """Retrieve a transaction from Redis"""
        if not self._redis:
            await self.init()
        
        # Get all fields from hash
        data = await self._redis.hgetall(f"transaction:{transaction_id}")
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

    async def set_sentinel_status(self, transaction_id: str, sentinel_name: str, status: str, result: Any = None) -> None:
        """Update a sentinel's status in the unified transaction record"""
        if not self._redis:
            await self.init()
        
        # Get current validations
        validations_json = await self._redis.hget(f"transaction:{transaction_id}", "validations")
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
            f"transaction:{transaction_id}", 
            "validations", 
            json.dumps(validations)
        )

    async def get_sentinel_statuses(self, transaction_id: str) -> Dict:
        """Get all sentinel statuses for a transaction from the unified structure"""
        transaction_data = await self.get_transaction(transaction_id)
        if not transaction_data:
            return {}
        
        sentinel_statuses = {}
        for validation in transaction_data.get("validations", []):
            if validation.get("name") != "agent":  # Exclude agent from sentinel results
                sentinel_statuses[validation.get("name")] = {
                    "status": validation.get("status"),
                    "result": validation.get("result", {})
                }
        
        return sentinel_statuses

    async def set_transaction_status(self, transaction_id: str, status: str):
        """Update transaction status and notify if completed"""
        if not self._redis:
            await self.init()
        
        key = f"transaction:{transaction_id}"
        
        # Update status and timestamp
        await self._redis.hset(key, mapping={
            "status": status,
            "updated_at": time.time()
        })
        
        # If COMPLETED, notify the persistence service
        if status == TransactionStatus.COMPLETED:
            await self.publish_message(
                self.settings.REDIS_CHANNELS.PERSISTENCE.value,
                {
                    "type": "persist_transaction",
                    "transaction_id": transaction_id,
                    "timestamp": time.time()
                }
            )
            logger.info(f"✅ Published persistence message for transaction {transaction_id}")

    async def set_agent_status(self, transaction_id: str, status: str, result: Any = None) -> None:
        """Set agent status in the unified transaction record"""
        await self.set_sentinel_status(transaction_id, "agent", status, result)

    async def get_agent_status(self, transaction_id: str) -> Optional[Dict]:
        """Get agent status from the unified transaction record"""
        transaction_data = await self.get_transaction(transaction_id)
        if not transaction_data:
            return None
        
        for validation in transaction_data.get("validations", []):
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

    async def get_all_transactions(self) -> List[str]:
        """Get all transaction IDs"""
        if not self._redis:
            await self.init()
        keys = await self._redis.keys("transaction:*")
        return [key.split(":")[1] for key in keys]

    async def get_transaction_details(self, transaction_id: str) -> Optional[dict]:
        """Get full transaction details - for backward compatibility"""
        return await self.get_transaction(transaction_id) 