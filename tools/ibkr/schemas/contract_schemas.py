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
    Validation schema for the dict response from /trsrv/stocks, keyed by symbol.
    """
    root: Dict[str, List[StockInfo]]

# --- Event Contracts (Forecast) schemas ---

class ForecastMarketItem(BaseModel):
    """
    Validation schema for a single market inside a category tree branch.
    """
    name: Optional[str] = Field(None, description="Name of the underlying market")
    symbol: Optional[str] = Field(None, description="Symbol")
    exchange: Optional[str] = Field(None, description="Listing exchange")
    is_restricted: Optional[bool] = Field(None, description="Is restricted flag")
    conid: Optional[Union[int, str]] = Field(None, description="Underlying ConID")
    product_conid: Optional[Union[int, str]] = Field(None, description="Product ConID")
    model_config = {"extra": "allow"}

class ForecastCategoryItem(BaseModel):
    """
    Validation schema for a single category branch in categories tree.
    """
    name: Optional[str] = Field(None, description="Category name")
    parent_id: Optional[str] = Field(None, description="Parent category ID")
    is_restricted: Optional[bool] = Field(None, description="Is restricted flag")
    markets: Optional[List[ForecastMarketItem]] = Field(default=[], description="Underlying markets")
    model_config = {"extra": "allow"}

class ForecastCategoryTreeResponse(BaseModel):
    """
    Validation schema for categories tree response from /forecast/category/tree.
    """
    categories: Optional[Dict[str, ForecastCategoryItem]] = Field(default={}, description="Forecast categories tree map")
    model_config = {"extra": "allow"}

class ForecastContractDetail(BaseModel):
    """
    Validation schema for forecast contract details response from /forecast/contract/details.
    """
    conid_yes: Optional[Union[int, str]] = Field(None, description="ConID for the 'Yes' outcome")
    conid_no: Optional[Union[int, str]] = Field(None, description="ConID for the 'No' outcome")
    question: Optional[str] = Field(None, description="Contract question details")
    side: Optional[str] = Field(None, description="Outcome side ('Y' or 'N')")
    strike_label: Optional[str] = Field(None, description="Strike threshold label")
    strike: Optional[float] = Field(None, description="Strike value")
    exchange: Optional[str] = Field(None, description="Listing exchange")
    expiration: Optional[str] = Field(None, description="Expiration date YYYYMMDD")
    symbol: Optional[str] = Field(None, description="Contract ticker symbol")
    category: Optional[str] = Field(None, description="Category identifier")
    logo_category: Optional[str] = Field(None, description="Logo category identifier")
    measured_period: Optional[str] = Field(None, description="Period of measurement")
    market_name: Optional[str] = Field(None, description="Market name")
    underlying_conid: Optional[Union[int, str]] = Field(None, description="Underlying market ConID")
    payout: Optional[float] = Field(None, description="Contract payout multiplier")
    product_conid: Optional[Union[int, str]] = Field(None, description="Product ConID")
    party: Optional[str] = Field(None, description="Associated political party or label")
    is_restricted: Optional[bool] = Field(None, description="Is restricted flag")
    model_config = {"extra": "allow"}

class ForecastMarketContract(BaseModel):
    """
    Validation schema for a specific contract trading within an underlying market.
    """
    conid: Optional[Union[int, str]] = Field(None, description="Contract outcome ConID")
    side: Optional[str] = Field(None, description="Outcome side ('Y' or 'N')")
    expiration: Optional[str] = Field(None, description="Expiration date YYYYMMDD")
    strike: Optional[float] = Field(None, description="Strike threshold value")
    strike_label: Optional[str] = Field(None, description="Strike threshold label")
    expiry_label: Optional[str] = Field(None, description="Expiry label")
    underlying_conid: Optional[Union[int, str]] = Field(None, description="Underlying ConID")
    time_specifier: Optional[str] = Field(None, description="Trading time specifier")
    party: Optional[str] = Field(None, description="Political party label")
    model_config = {"extra": "allow"}

class ForecastMarketResponse(BaseModel):
    """
    Validation schema for forecast underlying market response from /forecast/contract/market.
    """
    market_name: Optional[str] = Field(None, description="Market name")
    exchange: Optional[str] = Field(None, description="Listing exchange")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    logo_category: Optional[str] = Field(None, description="Logo category")
    exclude_historical_data: Optional[bool] = Field(None, description="Exclude historical data flag")
    payout: Optional[float] = Field(None, description="Payout value")
    contracts: Optional[List[ForecastMarketContract]] = Field(default=[], description="List of trade outcomes")
    model_config = {"extra": "allow"}

class ForecastPriceIncrement(BaseModel):
    """
    Validation schema for price increment step inside rules.
    """
    lower_edge: Optional[str] = Field(None, description="Lower edge value")
    increment: Optional[str] = Field(None, description="Price increment value")
    model_config = {"extra": "allow"}

class ForecastRulesResponse(BaseModel):
    """
    Validation schema for forecast rules response from /forecast/contract/rules.
    """
    asset_class: Optional[str] = Field(None, description="Asset class")
    description: Optional[str] = Field(None, description="Rule description")
    market_name: Optional[str] = Field(None, description="Market name")
    measured_period: Optional[str] = Field(None, description="Period of measurement")
    threshold: Optional[str] = Field(None, description="Rule threshold label")
    source_agency: Optional[str] = Field(None, description="Data source agency")
    data_and_resolution_link: Optional[str] = Field(None, description="Source resolution link")
    last_trade_time: Optional[int] = Field(None, description="Last trade time stamp")
    product_code: Optional[str] = Field(None, description="Product code")
    market_rules_link: Optional[str] = Field(None, description="Market rules PDF link")
    release_time: Optional[int] = Field(None, description="Release timestamp")
    payout_time: Optional[int] = Field(None, description="Payout timestamp")
    payout: Optional[str] = Field(None, description="Payout amount string")
    price_increment: Optional[str] = Field(None, description="Increment price string")
    price_increments: Optional[List[ForecastPriceIncrement]] = Field(default=[], description="List of increments")
    exchange_timezone: Optional[str] = Field(None, description="Exchange timezone")
    model_config = {"extra": "allow"}

class ForecastTradingTime(BaseModel):
    """
    Validation schema for a single opening/closing time slot inside a schedule.
    """
    open: Optional[str] = Field(None, description="Opening session time")
    close: Optional[str] = Field(None, description="Closing session time")
    model_config = {"extra": "allow"}

class ForecastTradingSchedule(BaseModel):
    """
    Validation schema for a daily forecast schedule.
    """
    day_of_week: Optional[str] = Field(None, description="Day of the week")
    trading_times: Optional[List[ForecastTradingTime]] = Field(default=[], description="Daily session hours")
    model_config = {"extra": "allow"}

class ForecastSchedulesResponse(BaseModel):
    """
    Validation schema for forecast schedules response from /forecast/contract/schedules.
    """
    timezone: Optional[str] = Field(None, description="Timezone name")
    trading_schedules: Optional[List[ForecastTradingSchedule]] = Field(default=[], description="Weekly schedule lists")
    model_config = {"extra": "allow"}

