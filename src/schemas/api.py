from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class TransactionRequest(BaseModel):
    chainId: int
    from_address: str
    to_address: str
    data: str
    value: str
    reason: Optional[str] = None

class TransactionResponse(BaseModel):
    request_id: str
    status: str = "processing" 
    results: Optional[dict] = None

class SentinelStatus(BaseModel):
    status: str
    result: Optional[dict] = None
    updated_at: Optional[str] = None

class RequestDetails(BaseModel):
    request_id: str
    status: str
    data: TransactionRequest
    created_at: str
    updated_at: Optional[str] = None
    sentinel_statuses: Dict[str, SentinelStatus] = {}

class DashboardResponse(BaseModel):
    total_requests: int
    active_requests: List[RequestDetails]
    completed_requests: List[RequestDetails]