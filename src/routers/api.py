from fastapi import APIRouter, HTTPException
from src.core import core
from src.schemas.api import TransactionRequest, TransactionResponse
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

@router.post("/transaction", response_model=TransactionResponse)
async def process_transaction(request: TransactionRequest):
    try:
        data = {
            "request_id": str(uuid.uuid4()),
            **request.model_dump()
        }
        logger.info(f"Processing transaction request: {data}")
        
        results = await core.analyze_transaction(data)
        return TransactionResponse(
            request_id=data["request_id"],
            results=results
        )
        
    except TimeoutError as e:
        logger.error(f"Request timeout: {e}")
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        logger.error(f"Error in API endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 