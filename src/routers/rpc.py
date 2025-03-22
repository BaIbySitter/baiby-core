from fastapi import APIRouter
from src.dispatcher import dispatcher
from src.schemas.rpc import RPCRequest, RPCResponse
import logging
import uuid
from src.core import core

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rpc")

@router.post("/transaction", response_model=RPCResponse)
async def process_transaction(rpc_request: RPCRequest):
    try:
        data = {
            "request_id": rpc_request.id or str(uuid.uuid4()),
            "method": rpc_request.method,
            **rpc_request.params
        }
        
        await core.process_request(data)
        return RPCResponse(
            id=data["request_id"],
            result={"status": "processing"}
        )
        
    except Exception as e:
        logger.error(f"Error in RPC endpoint: {e}")
        return RPCResponse(
            id=rpc_request.id,
            error={
                "code": -32603,
                "message": str(e)
            }
        ) 