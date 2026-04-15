"""
Pydantic schemas for IBKR Portfolio and Portfolio Analyst (PA) endpoints.
These models validate responses from /portfolio and /pa endpoints.
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

# --- Portfolio Schemas ---

class PortfolioAccount(BaseModel):
    """Schema for an account in the portfolio list."""
    id: str
    accountId: str
    accountVan: Optional[str] = None
    accountTitle: Optional[str] = None
    displayName: Optional[str] = None
    accountAlias: Optional[str] = None
    clearingStatus: Optional[str] = None
    name: Optional[str] = None
    baseCurrency: Optional[str] = None
    type: Optional[str] = None

class PortfolioAccountsResponse(BaseModel):
    """Response containing a list of portfolio accounts."""
    accounts: List[PortfolioAccount] = Field(default_factory=list)

class Position(BaseModel):
    """Schema for a single position in the portfolio."""
    acctId: str
    conid: int
    position: float
    mktPrice: float
    mktValue: float
    currency: str
    avgCost: float
    avgPrice: Optional[float] = None
    realizedPnl: Optional[float] = None
    unrealizedPnl: Optional[float] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    lastTradingDay: Optional[str] = None
    assetClass: Optional[str] = None
    expiry: Optional[str] = None
    putCall: Optional[str] = None
    strike: Optional[float] = None
    multiplier: Optional[float] = None

class PortfolioPositionsResponse(BaseModel):
    """Response containing a list of positions (paginated)."""
    positions: List[Position] = Field(default_factory=list)

class LedgerDetails(BaseModel):
    """Schema for currency-specific ledger details."""
    cashbalance: float = Field(alias="ca", default=0.0)
    stockvalue: float = Field(alias="se", default=0.0)
    netliquidation: float = Field(alias="ni", default=0.0)
    unrealizedpnl: float = Field(alias="un", default=0.0)
    realizedpnl: float = Field(alias="re", default=0.0)
    # Allowing extra fields as IBKR returns many single/two-letter keys
    class Config:
        extra = "allow"
        populate_by_name = True

class PortfolioLedgerResponse(BaseModel):
    """Response containing ledger information for multiple currencies."""
    ledger: Dict[str, LedgerDetails]

class SummaryItem(BaseModel):
    """Schema for a portfolio summary characteristic."""
    account: str
    key: str
    value: str
    valueDescription: Optional[str] = None
    baseCurrency: Optional[str] = None

class PortfolioSummaryResponse(BaseModel):
    """Response containing summary characteristics for an account."""
    summary: List[SummaryItem] = Field(default_factory=list)

class AllocationItem(BaseModel):
    """Schema for an allocation mapping (asset class, sector, etc.)."""
    group: str = Field(alias="group")
    value: float = Field(alias="val")
    percentage: float = Field(alias="pct")

class PortfolioAllocationResponse(BaseModel):
    """Response containing various allocation breakdowns."""
    assetClass: List[AllocationItem] = Field(alias="assetClass", default_factory=list)
    sector: List[AllocationItem] = Field(alias="sector", default_factory=list)
    grouping: List[AllocationItem] = Field(alias="grouping", default_factory=list)
    
    class Config:
        populate_by_name = True

# --- Portfolio Analyst (PA) Schemas ---

class PerformanceDataPoint(BaseModel):
    """Schema for a single performance data point (e.g., NAV or TWR)."""
    id: Optional[str] = None
    val: float = Field(alias="v")
    period: Optional[str] = Field(alias="p", default=None)

class PerformanceSeries(BaseModel):
    """Schema for a performance calculation series."""
    data: List[PerformanceDataPoint] = Field(default_factory=list)

class PAPerformanceResponse(BaseModel):
    """Response for Portfolio Analysis performance query."""
    id: Optional[str] = None
    nav: Optional[PerformanceSeries] = None
    twr: Optional[PerformanceSeries] = None
    # benchmarks, etc. can be added here
    class Config:
        extra = "allow"

class PASummaryResponse(BaseModel):
    """Response for Portfolio Analysis summary query."""
    # PA Summary often returns a nested structure of account info, PnL, etc.
    # For now, we allow extra to capture the dynamic nature.
    class Config:
        extra = "allow"

class PATransaction(BaseModel):
    """Schema for a historical transaction in Portfolio Analysis."""
    acctid: str
    conid: int
    symbol: str
    side: str
    qty: float
    pr: float
    amt: float
    comm: float
    date: str
    type: str

class PATransactionsResponse(BaseModel):
    """Response containing a list of transactions."""
    transactions: List[PATransaction] = Field(default_factory=list)
