"""
Pydantic schemas for IBKR Watchlist endpoints.
These models validate responses from /iserver/watchlists and /iserver/watchlist.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class WatchlistSummary(BaseModel):
    """
    Schema for a summary of a watchlist.
    """
    id: str
    name: str = Field(alias="name")
    type: str = Field(alias="type")

class WatchlistsResponse(BaseModel):
    """
    Response for /iserver/watchlists containing grouped summaries.
    """
    user_defined: List[WatchlistSummary] = Field(alias="USER", default_factory=list)
    system: List[WatchlistSummary] = Field(alias="SYST", default_factory=list)
    all_watchlists: List[WatchlistSummary] = Field(alias="ALL", default_factory=list)
    
    class Config:
        populate_by_name = True

class WatchlistRow(BaseModel):
    """
    Schema for a single row in a watchlist.
    """
    conid: Optional[int] = Field(None, alias="conid")
    symbol: Optional[str] = Field(None, alias="symbol")
    assetClass: Optional[str] = Field(None, alias="assetClass")
    type: Optional[str] = Field(None, alias="type")
    
    class Config:
        populate_by_name = True

class WatchlistDetail(BaseModel):
    """
    Response for /iserver/watchlist retrieving a specific watchlist.
    """
    id: str
    name: str
    rows: List[WatchlistRow] = Field(default_factory=list)

class WatchlistRequest(BaseModel):
    """
    Request body for creating or updating a watchlist.
    """
    name: str
    rows: List[WatchlistRow]
