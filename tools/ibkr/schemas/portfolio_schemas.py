"""
Pydantic schemas for IBKR Portfolio and Portfolio Analyst (PA) endpoints.
These models validate responses from /portfolio and /pa endpoints.
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, RootModel

# --- Portfolio Schemas ---

class PortfolioAccount(BaseModel):
    """Schema for an account in the portfolio list."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    accountId: Optional[str] = None
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

class PortfolioSubaccountsResponse(BaseModel):
    """Response containing a list of sub-accounts."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    subaccounts: List[PortfolioAccount] = Field(default_factory=list)

class PortfolioAccountMetaResponse(BaseModel):
    """Response containing account metadata/attributes."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: Optional[str] = None
    accountId: Optional[str] = None
    displayName: Optional[str] = None
    clearingStatus: Optional[str] = None
    baseCurrency: Optional[str] = Field(alias="currency", default=None)

class Position(BaseModel):
    """Schema for a single position in the portfolio."""
    model_config = ConfigDict(extra="allow")
    acctId: Optional[str] = None
    conid: Optional[int] = None
    position: Optional[float] = None
    mktPrice: Optional[float] = None
    mktValue: Optional[float] = None
    currency: Optional[str] = None
    avgCost: Optional[float] = None
    avgPrice: Optional[float] = None
    realizedPnl: Optional[float] = None
    unrealizedPnl: Optional[float] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    lastTradingDay: Optional[str] = None
    assetClass: Optional[str] = None
    expiry: Optional[str] = None
    putCall: Optional[str] = None
    strike: Optional[Union[float, str]] = None
    multiplier: Optional[float] = None

class PortfolioPositionsResponse(BaseModel):
    """Response containing a list of positions (paginated)."""
    positions: List[Position] = Field(default_factory=list)

class PortfolioPositionResponse(BaseModel):
    """Response containing position details for a specific conid."""
    model_config = ConfigDict(extra="allow")
    positions: List[Position] = Field(default_factory=list)

class PortfolioPositionsConidResponse(RootModel[Dict[str, List[Position]]]):
    """Response containing positions across accounts for a conid (mapped by accountId)."""
    pass

class LedgerDetails(BaseModel):
    """Schema for currency-specific ledger details."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    cashbalance: float = Field(alias="ca", default=0.0)
    stockvalue: float = Field(alias="se", default=0.0)
    netliquidation: float = Field(alias="ni", default=0.0)
    unrealizedpnl: float = Field(alias="un", default=0.0)
    realizedpnl: float = Field(alias="re", default=0.0)

class PortfolioLedgerResponse(BaseModel):
    """Response containing ledger information for multiple currencies."""
    ledger: Dict[str, LedgerDetails]

class SummaryValue(BaseModel):
    """Schema for a portfolio summary value."""
    model_config = ConfigDict(extra="allow")
    amount: float = 0.0
    currency: Optional[str] = None
    isNull: bool = False
    timestamp: int = 0
    value: Optional[Union[str, float, bool]] = None
    severity: int = 0

class PortfolioSummaryResponse(BaseModel):
    """Response containing summary characteristics for an account."""
    summary: Dict[str, SummaryValue] = Field(default_factory=dict)

class AllocationItem(BaseModel):
    """Schema for an allocation mapping (asset class, sector, etc.)."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    group: Optional[str] = Field(alias="group", default=None)
    value: Optional[float] = Field(alias="val", default=None)
    percentage: Optional[float] = Field(alias="pct", default=None)

class AllocationBreakdown(BaseModel):
    """Schema for a nested allocation breakdown (e.g. long/short sectors/asset classes)."""
    model_config = ConfigDict(extra="allow")
    long: Dict[str, float] = Field(default_factory=dict)
    short: Dict[str, float] = Field(default_factory=dict)

class PortfolioAllocationResponse(BaseModel):
    """Response containing various allocation breakdowns."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    assetClass: Optional[Union[List[AllocationItem], AllocationBreakdown, Dict[str, Any]]] = Field(alias="assetClass", default=None)
    sector: Optional[Union[List[AllocationItem], AllocationBreakdown, Dict[str, Any]]] = Field(alias="sector", default=None)
    group: Optional[Union[List[AllocationItem], AllocationBreakdown, Dict[str, Any]]] = Field(alias="group", default=None)
    grouping: Optional[Union[List[AllocationItem], AllocationBreakdown, Dict[str, Any]]] = Field(alias="grouping", default=None)

# --- Portfolio Analyst (PA) Schemas ---

class PerformanceDataPoint(BaseModel):
    """Schema for a single performance data point (e.g., NAV or TWR)."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: Optional[str] = None
    val: Optional[float] = Field(alias="v", default=None)
    period: Optional[str] = Field(alias="p", default=None)

class PerformanceSeries(BaseModel):
    """Schema for a performance calculation series."""
    data: List[PerformanceDataPoint] = Field(default_factory=list)

class PAPerformanceResponse(BaseModel):
    """Response for Portfolio Analysis performance query."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    nav: Optional[PerformanceSeries] = None
    twr: Optional[PerformanceSeries] = None
    # benchmarks, etc. can be added here

class PASummaryResponse(BaseModel):
    """Response for Portfolio Analysis summary query."""
    # PA Summary often returns a nested structure of account info, PnL, etc.
    # For now, we allow extra to capture the dynamic nature.
    model_config = ConfigDict(extra="allow")

class PAAllocationDetailItem(BaseModel):
    """Schema for a single allocation detail item (e.g. STK, Equities, etc.)."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    name: Optional[str] = None
    nav: Optional[float] = None
    weight: Optional[float] = None
    color: Optional[str] = None

class PAAllocationTotal(BaseModel):
    """Schema for total nav and weight of a direction."""
    model_config = ConfigDict(extra="allow")
    nav: Optional[float] = None
    weight: Optional[float] = None

class PAAllocationDirectionDetail(BaseModel):
    """Schema for a direction (long or short) allocation detail."""
    model_config = ConfigDict(extra="allow")
    total: Optional[PAAllocationTotal] = None
    items: List[PAAllocationDetailItem] = Field(default_factory=list)

class PAAllocationTypeBreakdown(BaseModel):
    """Schema for long and short allocations of a category type."""
    model_config = ConfigDict(extra="allow")
    long: Optional[PAAllocationDirectionDetail] = None
    short: Optional[PAAllocationDirectionDetail] = None

class PAAllocationResponse(BaseModel):
    """Response containing consolidated portfolio analyst allocation data."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    currency: Optional[str] = None
    realtime: Optional[bool] = None
    date: Optional[str] = None
    allocations: Dict[str, PAAllocationTypeBreakdown] = Field(default_factory=dict)

class PATransaction(BaseModel):
    """Schema for a historical transaction in Portfolio Analysis."""
    model_config = ConfigDict(extra="allow")
    acctid: Optional[str] = None
    conid: Optional[int] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    qty: Optional[float] = None
    pr: Optional[float] = None
    amt: Optional[float] = None
    comm: Optional[float] = None
    date: Optional[str] = None
    type: Optional[str] = None

class PATransactionsResponse(BaseModel):
    """Response containing a list of transactions."""
    transactions: List[PATransaction] = Field(default_factory=list)
