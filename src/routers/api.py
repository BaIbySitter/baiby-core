from fastapi import APIRouter, HTTPException
from src.core import core
from src.schemas.api import TransactionRequest, TransactionResponse, RequestDetails, StatusResponse, DashboardResponse
import logging
import uuid
from datetime import datetime
from src.state_manager import StateManager
from src.constants import RequestStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

@router.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}

@router.post("/transaction", response_model=TransactionResponse)
async def process_transaction(request: TransactionRequest):
    try:
        data = {
            "request_id": str(uuid.uuid4()),
            **request.model_dump()
        }
        logger.info(f"⚡ Processing transaction request: {data}")
        
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

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    try:
        state = StateManager()
        request_ids = await state.get_all_requests()
        
        requests = []
        for request_id in request_ids:
            details = await state.get_request_details(request_id)
            if details:
                # Convertir timestamps a strings ISO antes de crear el modelo
                if 'created_at' in details:
                    details['created_at'] = datetime.fromtimestamp(float(details['created_at'])).isoformat()
                if 'updated_at' in details and details['updated_at']:
                    details['updated_at'] = datetime.fromtimestamp(float(details['updated_at'])).isoformat()
                
                requests.append(RequestDetails(**details))

        # Split into active and completed
        active = [r for r in requests if r.status != RequestStatus.COMPLETED]
        completed = [r for r in requests if r.status == RequestStatus.COMPLETED]

        return DashboardResponse(
            total_requests=len(requests),
            active_requests=active,
            completed_requests=completed
        )

    except Exception as e:
        logger.error(f"Error in dashboard endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction/{request_id}", response_model=RequestDetails)
async def get_transaction(request_id: str):
    try:
        state = StateManager()
        details = await state.get_request_details(request_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Convertir timestamps a strings ISO
        if 'created_at' in details:
            details['created_at'] = datetime.fromtimestamp(float(details['created_at'])).isoformat()
        if 'updated_at' in details and details['updated_at']:
            details['updated_at'] = datetime.fromtimestamp(float(details['updated_at'])).isoformat()
            
        return RequestDetails(**details)

    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        raise HTTPException(status_code=500, detail=str(e))
