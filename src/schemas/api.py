from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class TransactionRequest(BaseModel):
    chainId: int
    from_address: str
    to_address: str
    data: str
    value: str = "0"
    reason: Optional[str] = None

class TransactionResponse(BaseModel):
    request_id: str
    status: str
    result: Dict[str, Any]

class ValidationResult(BaseModel):
    name: str
    status: str
    result: Optional[Dict[str, Any]] = None

class SentinelStatus(BaseModel):
    status: str
    result: Optional[dict] = None
    updated_at: Optional[str] = None

class RequestDetails(BaseModel):
    request_id: str
    chainId: int
    from_address: str
    to_address: str
    data: str
    value: int
    reason: Optional[str] = None
    validations: List[ValidationResult]
    created_at: Union[str, float]
    updated_at: Optional[Union[str, float]] = None
    status: str

class DashboardResponse(BaseModel):
    total_requests: int
    active_requests: List[RequestDetails]
    completed_requests: List[RequestDetails]