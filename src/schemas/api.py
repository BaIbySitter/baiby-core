from pydantic import BaseModel
from typing import Optional

class TransactionRequest(BaseModel):
    chainId: int
    from_address: str  # using from_address since 'from' is a Python keyword
    to: str
    data: str
    value: str
    reason: Optional[str] = None

class TransactionResponse(BaseModel):
    request_id: str
    status: str = "processing" 
    results: Optional[dict] = None