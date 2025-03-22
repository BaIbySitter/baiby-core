import json
import logging
import asyncio
from src.warning_manager import warning_manager
from src.sentinel_coordinator import coordinator

logger = logging.getLogger(__name__)

async def handle_api_incoming_message(message, broker):
    try:
        data = json.loads(message['data'])
        await asyncio.sleep(5)
        await broker.publish_response("api_gateway", {
            "request_id": data.get("txHash"),
            "data": data
        })
        # Dispatch to sentinels and wait for their analysis
        await coordinator.dispatch_to_sentinels(data)
                
    except Exception as e:
        logger.error(f"Error processing API incoming message: {e}") 