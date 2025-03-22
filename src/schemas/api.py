from pydantic import BaseModel
from typing import Optional, Dict, Any

class TransactionRequest(BaseModel):
    transaction_hash: str
    address: str
    data: Optional[Dict[str, Any]] = None
    
class TransactionResponse(BaseModel):
    request_id: str
    status: str = "processing" 