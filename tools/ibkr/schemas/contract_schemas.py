"""
Pydantic schemas for the IBKR Contract tool.
This module defines the validation models for contract-related data
as specified in the Interactive Brokers Client Portal API documentation.
"""
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any, Union

class ContractSearchSection(BaseModel):
    """
    Validation schema for derivative sections in a contract search result.
    """
    secType: Optional[str] = Field(None, description="Asset class (e.g., STK, OPT, FUT)")
    months: Optional[str] = Field(None, description="Available expiration months (for derivatives)")
    exchange: Optional[str] = Field(None, description="Exchanges where it trades")
    model_config = {"extra": "allow"}

class ContractSearchResult(BaseModel):
    """
    Validation schema for a single search result from /iserver/secdef/search.
    """
    conid: Union[int, str] = Field(..., description="Unique contract identifier")
    companyName: Optional[str] = Field(None, description="Company or instrument name")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    description: Optional[str] = Field(None, description="Listing info/exchange")
    companyHeader: Optional[str] = Field(None, description="Formatted company header")
    sections: List[ContractSearchSection] = Field(default=[], description="Available derivative classes")
    model_config = {"extra": "allow"}

class ContractSearchResponse(RootModel):
    """
    Validation schema for the list response from /iserver/secdef/search.
    """
    root: List[ContractSearchResult]

class ContractInfo(BaseModel):
    """
    Validation schema for detailed contract information from /iserver/secdef/info.
    """
    conid: Union[int, str] = Field(..., description="Contract ID")
    companyName: Optional[str] = Field(None, description="Full company name")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    secType: Optional[str] = Field(None, description="Security type")
    exchange: Optional[str] = Field(None, description="Exchange name")
    currency: Optional[str] = Field(None, description="Currency (e.g., USD)")
    multiplier: Optional[str] = Field(None, description="Contract multiplier")
    strike: Optional[Any] = Field(None, description="Strike price (for options)")
    right: Optional[str] = Field(None, description="C or P (for options)")
    maturityDate: Optional[str] = Field(None, description="Maturity/Expiration date")
    description: Optional[str] = Field(None, description="Instrument description")
    tradingClass: Optional[str] = Field(None, description="Trading class identifier")
    validExchanges: Optional[Any] = Field(None, description="List of valid exchanges")
    model_config = {"extra": "allow"}

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
    model_config = {"extra": "allow"}

class TradingSession(BaseModel):
    """
    Validation schema for a single trading session.
    """
    openingTime: Optional[str] = Field(None, description="Session start time")
    closingTime: Optional[str] = Field(None, description="Session end time")
    prop: Optional[str] = Field(None, description="Session property (e.g., RTH, LIQUID)")
    model_config = {"extra": "allow"}

class TradingSchedule(BaseModel):
    """
    Validation schema for a contract's trading schedule.
    """
    id: Optional[str] = Field(None, description="Schedule identifier")
    tradingScheduleDate: Optional[int] = Field(None, description="Date of the schedule")
    sessions: Optional[List[TradingSession]] = Field(default=[], description="Daily trading sessions")
    tradingDayOpeningTime: Optional[int] = Field(None, description="Day opening time")
    tradingDayClosingTime: Optional[int] = Field(None, description="Day closing time")
    schedules: Optional[List[Dict[str, Any]]] = Field(None, description="Nested schedules list if present")
    model_config = {"extra": "allow"}

class TradingScheduleResponse(RootModel):
    """
    Validation schema for the list response from /iserver/secdef/schedule.
    """
    root: List[TradingSchedule]

class ContractTradingScheduleResponse(BaseModel):
    """
    Validation schema for response from /contract/trading-schedule.
    """
    exchange_time_zone: Optional[str] = Field(None, description="Exchange timezone")
    schedules: Optional[Dict[str, Any]] = Field(None, description="Daily trading schedules mapping")
    model_config = {"extra": "allow"}

class ContractRulesResponse(BaseModel):
    """
    Validation schema for contract rules from /iserver/contract/rules or info-and-rules.
    """
    rules: Optional[Dict[str, Any]] = Field(None, description="Detailed trading rules")
    orderTypes: Optional[List[str]] = Field(None, description="Supported order types")
    tifTypes: Optional[List[str]] = Field(None, description="Supported time-in-force types")
    model_config = {"extra": "allow"}

class AlgoParam(BaseModel):
    """
    Validation schema for a single parameter of an algorithm.
    """
    id: str = Field(..., description="Parameter identifier")
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter data type")
    description: Optional[str] = Field(None, description="Parameter description")
    model_config = {"extra": "allow"}

class AlgoInfo(BaseModel):
    """
    Validation schema for an algorithm strategy.
    """
    id: str = Field(..., description="Algorithm identifier")
    name: str = Field(..., description="Algorithm name")
    parameters: Optional[List[AlgoParam]] = Field(None, description="Required/optional parameters")
    description: Optional[str] = Field(None, description="Algorithm strategy description")
    model_config = {"extra": "allow"}

class AlgosResponse(BaseModel):
    """
    Validation schema for the response from /iserver/contract/{conid}/algos.
    """
    algos: Optional[List[AlgoInfo]] = Field(default=[], description="List of algorithms")
    model_config = {"extra": "allow"}

class InstrumentInfoResponse(BaseModel):
    """
    Validation schema for response from /iserver/contract/{conid}/info.
    """
    rT: Optional[int] = Field(None, description="Response type or timestamp")
    companyName: Optional[str] = Field(None, description="Full company name")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    conid: Optional[Union[int, str]] = Field(None, description="Contract ID")
    model_config = {"extra": "allow"}

class InfoAndRulesResponse(BaseModel):
    """
    Validation schema for response from /iserver/contract/{conid}/info-and-rules.
    """
    info: Optional[InstrumentInfoResponse] = Field(None, description="Detailed instrument info")
    rules: Optional[Dict[str, Any]] = Field(None, description="Trading rules associated with this instrument")
    model_config = {"extra": "allow"}

class CurrencyPairInfo(BaseModel):
    """
    Validation schema for currency pair info list item.
    """
    symbol: Optional[str] = Field(None, description="Currency pair symbol")
    conid: Optional[Union[int, str]] = Field(None, description="Contract ID")
    ccyPair: Optional[str] = Field(None, description="Opposite currency code")
    model_config = {"extra": "allow"}

class CurrencyPairsResponse(RootModel):
    """
    Validation schema for the response from /iserver/currency/pairs.
    """
    root: Dict[str, List[CurrencyPairInfo]]

class ExchangeRateResponse(BaseModel):
    """
    Validation schema for currency exchange rate from /iserver/exchangerate.
    """
    rate: float = Field(..., description="The current exchange rate")
    source: Optional[str] = Field(None, description="Base currency")
    target: Optional[str] = Field(None, description="Quote currency")
    model_config = {"extra": "allow"}

class BondFilterOption(BaseModel):
    """
    Validation schema for an option value inside a bond filter.
    """
    text: Optional[str] = Field(None, description="Display text for the option")
    value: Union[str, float, int] = Field(..., description="Option value")
    model_config = {"extra": "allow"}

class BondFilter(BaseModel):
    """
    Validation schema for bond filters from /iserver/secdef/bond-filters.
    """
    displayText: Optional[str] = Field(None, description="Display name of the filter category")
    columnId: Optional[int] = Field(None, description="Unique column ID")
    options: Optional[List[BondFilterOption]] = Field(default=[], description="List of filter options")
    model_config = {"extra": "allow"}

class BondFiltersResponse(BaseModel):
    """
    Validation schema for the response from /iserver/secdef/bond-filters.
    """
    bondFilters: Optional[List[BondFilter]] = Field(default=[], description="List of bond filters")
    model_config = {"extra": "allow"}

class ExchangeConidInfo(BaseModel):
    """
    Validation schema for stock contract details tradable on an exchange.
    """
    ticker: Optional[str] = Field(None, description="Ticker symbol")
    conid: Optional[Union[int, str]] = Field(None, description="Contract ID")
    exchange: Optional[str] = Field(None, description="Exchange")
    model_config = {"extra": "allow"}

class AllConidsResponse(RootModel):
    """
    Validation schema for response from /trsrv/all-conids.
    """
    root: List[ExchangeConidInfo]

class FutureInfo(BaseModel):
    """
    Validation schema for a single future contract from /trsrv/futures.
    """
    symbol: str = Field(..., description="Security symbol")
    conid: Union[int, str] = Field(..., description="Unique contract identifier")
    underlyingConid: Optional[Union[int, str]] = Field(None, description="Underlying contract ID")
    expirationDate: Optional[int] = Field(None, description="Contract expiration date YYYYMMDD")
    ltd: Optional[int] = Field(None, description="Last trading day")
    model_config = {"extra": "allow"}

class FuturesResponse(RootModel):
    """
    Validation schema for the dict response from /trsrv/futures, keyed by symbol.
    """
    root: Dict[str, List[FutureInfo]]

class TrsrvSecdefInfo(BaseModel):
    """
    Validation schema for a single security definition from /trsrv/secdef.
    """
    conid: Union[int, str] = Field(..., description="Unique contract identifier")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    ticker: Optional[str] = Field(None, description="Ticker symbol alias")
    secType: Optional[str] = Field(None, description="Security type")
    assetClass: Optional[str] = Field(None, description="Security type alias")
    exchange: Optional[str] = Field(None, description="Primary exchange")
    listingExchange: Optional[str] = Field(None, description="Listing exchange alias")
    currency: Optional[str] = Field(None, description="Trading currency")
    model_config = {"extra": "allow"}

class TrsrvSecdefResponse(BaseModel):
    """
    Validation schema for the response from /trsrv/secdef.
    """
    secdef: Optional[List[TrsrvSecdefInfo]] = Field(default=[], description="List of security definitions")
    model_config = {"extra": "allow"}

class StockContractInfo(BaseModel):
    """
    Validation schema for single contract detail in stock query.
    """
    conid: Optional[Union[int, str]] = Field(None, description="Contract ID")
    exchange: Optional[str] = Field(None, description="Exchange")
    isUS: Optional[bool] = Field(None, description="Is US contract")
    model_config = {"extra": "allow"}

class StockInfo(BaseModel):
    """
    Validation schema for a stock contract from /trsrv/stocks.
    """
    name: Optional[str] = Field(None, description="Company name")
    assetClass: Optional[str] = Field(None, description="Asset class")
    contracts: Optional[List[StockContractInfo]] = Field(default=[], description="Available contracts")
    model_config = {"extra": "allow"}

class StocksResponse(RootModel):
    """
    Validation schema for response from /trsrv/stocks, keyed by symbol.
    """
    root: Dict[str, List[StockInfo]]
