"""
Pydantic schemas for the IBKR Contract tool.
This module defines the validation models for contract-related data
as specified in the Interactive Brokers Client Portal API documentation.
"""
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any

class ContractSearchSection(BaseModel):
    """
    Validation schema for derivative sections in a contract search result.
    """
    secType: str = Field(..., description="Asset class (e.g., STK, OPT, FUT)")
    months: Optional[str] = Field(None, description="Available expiration months (for derivatives)")
    exchange: Optional[str] = Field(None, description="Exchanges where it trades")

class ContractSearchResult(BaseModel):
    """
    Validation schema for a single search result from /iserver/secdef/search.
    """
    conid: str = Field(..., description="Unique contract identifier")
    companyName: str = Field(..., description="Company or instrument name")
    symbol: str = Field(..., description="Ticker symbol")
    description: Optional[str] = Field(None, description="Listing info/exchange")
    companyHeader: Optional[str] = Field(None, description="Formatted company header")
    sections: List[ContractSearchSection] = Field(default=[], description="Available derivative classes")

class ContractSearchResponse(RootModel):
    """
    Validation schema for the list response from /iserver/secdef/search.
    """
    root: List[ContractSearchResult]

class ContractInfo(BaseModel):
    """
    Validation schema for detailed contract information from /iserver/secdef/info.
    """
    conid: str = Field(..., description="Contract ID")
    companyName: str = Field(..., description="Full company name")
    symbol: str = Field(..., description="Ticker symbol")
    secType: str = Field(..., description="Security type")
    exchange: str = Field(..., description="Exchange name")
    currency: str = Field(..., description="Currency (e.g., USD)")
    multiplier: Optional[str] = Field(None, description="Contract multiplier")
    strike: Optional[str] = Field(None, description="Strike price (for options)")
    right: Optional[str] = Field(None, description="C or P (for options)")
    maturityDate: Optional[str] = Field(None, description="Maturity/Expiration date")
    description: Optional[str] = Field(None, description="Instrument description")
    tradingClass: Optional[str] = Field(None, description="Trading class identifier")
    validExchanges: Optional[List[str]] = Field(None, description="List of valid exchanges")

class ContractInfoResponse(RootModel):
    """
    Validation schema for the list response from /iserver/secdef/info.
    """
    root: List[ContractInfo]

class StrikesResponse(BaseModel):
    """
    Validation schema for option strikes from /iserver/secdef/strikes.
    """
    call: List[float] = Field(default=[], description="Available call strikes")
    put: List[float] = Field(default=[], description="Available put strikes")

class TradingSession(BaseModel):
    """
    Validation schema for a single trading session.
    """
    openingTime: str = Field(..., description="Session start time")
    closingTime: str = Field(..., description="Session end time")
    prop: str = Field(..., description="Session property (e.g., RTH, LIQUID)")

class TradingSchedule(BaseModel):
    """
    Validation schema for a contract's trading schedule.
    """
    id: str = Field(..., description="Schedule identifier")
    tradingScheduleDate: int = Field(..., description="Date of the schedule")
    sessions: List[TradingSession] = Field(..., description="Daily trading sessions")
    tradingDayOpeningTime: int = Field(..., description="Day opening time")
    tradingDayClosingTime: int = Field(..., description="Day closing time")

class TradingScheduleResponse(RootModel):
    """
    Validation schema for the list response from /iserver/secdef/tradingschedule.
    """
    root: List[TradingSchedule]
