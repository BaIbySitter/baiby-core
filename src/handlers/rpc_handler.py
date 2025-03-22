import json
import logging
from src.sentinel_coordinator import coordinator

logger = logging.getLogger(__name__)

async def handle_rpc_incoming_message(message, broker):
    try:
        data = json.loads(message['data'])
        # Dispatch to sentinels and wait for their analysis
        await coordinator.dispatch_to_sentinels(data)
                
    except Exception as e:
        logger.error(f"Error processing RPC incoming message: {e}") 