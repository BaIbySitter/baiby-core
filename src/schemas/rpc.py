from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class RPCRequest(BaseModel):
    jsonrpc: str = Field("2.0", const=True)
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

class RPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None 