"""
Pydantic schemas for IBKR Session endpoints.
These models validate responses from /iserver/auth/status, /tickle, etc.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AuthStatus(BaseModel):
    """
    Schema for the /iserver/auth/status response.
    """
    authenticated: bool
    connected: bool
    competing: bool
    fail: Optional[str] = None
    message: Optional[str] = None
    prompts: List[str] = Field(default_factory=list)

class TickleResponse(BaseModel):
    """
    Schema for the /tickle response.
    """
    session: str
    ssoExpires: int
    collateral: bool
    iserver: Dict[str, Any]
