from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

class TransactionRequest(BaseModel):
    chainId: int
    from_address: str
    to_address: str
    data: str
    value: str = "0"
    reason: Optional[str] = None

class TransactionResponse(BaseModel):
    transaction_id: str
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

class TransactionDetail(BaseModel):
    transaction_id: str
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

class TransactionSummary(BaseModel):
    """Modelo resumido de transacción para el dashboard"""
    transaction_id: str
    from_address: str
    created_at: Union[str, float]
    status: str

class DashboardResponse(BaseModel):
    total_transactions: int
    active_transactions: List[TransactionSummary]
    completed_transactions: List[TransactionSummary]