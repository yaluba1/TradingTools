"""
Pydantic schemas for IBKR Session endpoints.
These models validate responses from /iserver/auth/status, /tickle, etc.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

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
    collateral: Optional[bool] = None
    iserver: Dict[str, Any]

class SSOValidateResponse(BaseModel):
    """
    Schema for the /sso/validate response.
    """
    model_config = ConfigDict(extra="allow")

    LOGIN_TYPE: Optional[int] = None
    USER_NAME: Optional[str] = None
    USER_ID: Optional[int] = None
    expire: Optional[int] = None
    EXPIRES: Optional[int] = None
    RESULT: Optional[bool] = None
    AUTH_TIME: Optional[int] = None

