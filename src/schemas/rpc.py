from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal

class RPCRequest(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

class RPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None 