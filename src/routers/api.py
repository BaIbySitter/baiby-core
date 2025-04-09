from fastapi import APIRouter, HTTPException
from src.core import core
from src.schemas.api import TransactionRequest, TransactionResponse, DashboardResponse, TransactionDetail, TransactionSummary
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

@router.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """Get summarized dashboard statistics and transaction headers"""
    try:
        from src.persistence_service import get_persistence_service
        persistence = get_persistence_service()
        
        # Get summarized dashboard data
        active_transactions_data, completed_transactions_data, total_count = await persistence.get_transactions_data()
        
        # Convert data to Pydantic objects
        active_transactions = [TransactionSummary(**tx) for tx in active_transactions_data]
        completed_transactions = [TransactionSummary(**tx) for tx in completed_transactions_data]
        
        return DashboardResponse(
            total_transactions=total_count,
            active_transactions=active_transactions,
            completed_transactions=completed_transactions
        )
    except Exception as e:
        logger.error(f"Error in dashboard endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction/{transaction_id}", response_model=TransactionDetail)
async def get_transaction(transaction_id: str):
    """Get transaction details from persistence service"""
    try:
        from src.persistence_service import get_persistence_service
        persistence = get_persistence_service()
        
        # Get transaction details from persistence service
        transaction = await persistence.get_transaction_details(transaction_id)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        return TransactionDetail(**transaction)
    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction", response_model=TransactionResponse)
async def process_transaction(request: TransactionRequest):
    try:
        data = request.model_dump()
        logger.info(f"⚡ Processing transaction: {data}")
        
        result = await core.analyze_transaction(data)
        return TransactionResponse(
            transaction_id=result.get("transaction_id"),
            status=result.get("status"),
            result=result
        )
        
    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        logger.error(f"Error in API endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))