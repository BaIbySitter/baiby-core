from abc import ABC, abstractmethod
import json
import logging
import asyncio
from src.config import get_settings

logger = logging.getLogger(__name__)

class BaseSentinel(ABC):
    def __init__(self):
        self.settings = get_settings()
        self.redis = None
        self.name = self.__class__.__name__

    async def connect(self):
        from src.message_broker import broker
        self.redis = broker.redis
        logger.info(f"Sentinel {self.name} connected")

    @abstractmethod
    async def analyze(self, data: dict) -> dict:
        """Each sentinel must implement its own analysis logic"""
        pass

    async def listen(self):
        if not self.redis:
            await self.connect()

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.settings.REDIS_CHANNELS.SENTINELS_INPUT)
        logger.info(f"Sentinel {self.name} listening")

        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = json.loads(message['data'])
                    analysis = await self.analyze(data)
                    
                    # Send response back to coordinator
                    response = {
                        "sentinel": self.name,
                        "request_id": data.get("request_id"),
                        "analysis": analysis
                    }
                    await self.redis.publish(self.settings.REDIS_CHANNELS.SENTINELS_OUTPUT,
                        json.dumps(response)
                    )
            except Exception as e:
                logger.error(f"Error in sentinel {self.name}: {e}")
            await asyncio.sleep(0.01) 