from fastapi import APIRouter, HTTPException
from src.core import core
from src.schemas.rpc import RPCRequest, RPCResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rpc")

@router.post("/transaction", response_model=RPCResponse)
async def process_transaction(request: RPCRequest):
    try:
        data = request.model_dump()
        logger.info(f"⚡ Processing transaction: {data}")
        
        result = await core.analyze_transaction(data)

        return RPCResponse(
            transaction_id=result.get("transaction_id"),
            status="completed",
            result=result
        )
        
    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        logger.error(f"Error in API endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))