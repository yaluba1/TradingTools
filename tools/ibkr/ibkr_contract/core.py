"""
Core logic for the IBKR Contract tool.
This module provides the ContractManager class to interact with IBKR contract endpoints,
supporting security search, detailed info retrieval, strikes, and trading schedules.
"""
from typing import List, Dict, Any, Optional
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..schemas.contract_schemas import (
    ContractSearchResponse,
    ContractInfoResponse,
    StrikesResponse,
    TradingScheduleResponse,
    ContractTradingScheduleResponse,
    ContractRulesResponse,
    AlgosResponse,
    InstrumentInfoResponse,
    InfoAndRulesResponse,
    CurrencyPairsResponse,
    ExchangeRateResponse,
    BondFiltersResponse,
    AllConidsResponse,
    FuturesResponse,
    TrsrvSecdefResponse,
    StocksResponse,
    ForecastCategoryTreeResponse,
    ForecastContractDetail,
    ForecastMarketResponse,
    ForecastRulesResponse,
    ForecastSchedulesResponse
)

class ContractManager:
    """
    Manager for IBKR contract-related operations.
    
    This class wraps the /iserver/secdef, /iserver/contract, /iserver/currency, and /trsrv
    endpoints, ensuring all searches, schedule queries, definitions, rules, and details retrieval 
    are logged and validated.
    """
    def __init__(self):
        """
        Initialize the ContractManager.
        
        Sets up the API client with pacing support and the logger for file recording.
        """
        self.tool_name = "contract"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def search_contracts(self, symbol: str, secType: Optional[str] = None, name: Optional[bool] = None, more: Optional[bool] = None, referrer: Optional[str] = None) -> ContractSearchResponse:
        """
        Search for a security definition by symbol.
        
        Args:
            symbol (str): The ticker symbol to search for (e.g., 'AAPL').
            secType (Optional[str]): Asset class filter (e.g., STK, OPT, FUT).
            name (Optional[bool]): If True, search will also look in company name.
            more (Optional[bool]): If True, returns more results.
            referrer (Optional[str]): Referrer source.
            
        Returns:
            ContractSearchResponse: Validated list of matching contracts.
        """
        self.logger.info(f"Searching for contracts with symbol: {symbol}")
        endpoint = "/iserver/secdef/search"
        payload = {"symbol": symbol}
        if secType is not None:
            payload["secType"] = secType
        if name is not None:
            payload["name"] = name
        if more is not None:
            payload["more"] = more
        if referrer is not None:
            payload["referrer"] = referrer

        try:
            data = self.client.post(endpoint, json_data=payload)
            response = ContractSearchResponse(data)
            self.logger.log_action(
                "search_contracts",
                message=f"Found {len(response.root)} results for {symbol}.",
                details={"symbol": symbol, "secType": secType, "count": len(response.root)}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to search contracts for {symbol}: {e}")
            raise

    def get_contract_details(self, conid: str, sectype: Optional[str] = None, month: Optional[str] = None, exchange: Optional[str] = None, strike: Optional[float] = None, right: Optional[str] = None) -> ContractInfoResponse:
        """
        Retrieve detailed attributes for a specific contract.
        
        Args:
            conid (str): The contract ID.
            sectype (Optional[str]): The security type (e.g. 'STK').
            month (Optional[str]): Contract month (e.g. 'OCT24').
            exchange (Optional[str]): Exchange.
            strike (Optional[float]): Strike price.
            right (Optional[str]): C or P.
            
        Returns:
            ContractInfoResponse: Validated detailed contract info.
        """
        self.logger.info(f"Fetching details for conid: {conid}")
        endpoint = "/iserver/secdef/info"
        params = {"conid": conid}
        if sectype is not None:
            params["sectype"] = sectype
        if month is not None:
            params["month"] = month
        if exchange is not None:
            params["exchange"] = exchange
        if strike is not None:
            params["strike"] = str(strike)
        if right is not None:
            params["right"] = right

        try:
            data = self.client.get(endpoint, params=params)
            # Ensure the response is always a list for ContractInfoResponse RootModel
            if isinstance(data, dict):
                data = [data]
            response = ContractInfoResponse(data)
            self.logger.log_action(
                "get_contract_details",
                message=f"Retrieved info for conid {conid}.",
                details={"conid": conid, "sectype": sectype}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch contract details for {conid}: {e}")
            raise

    def get_strikes(self, conid: str, sectype: str, month: str, exchange: str = "SMART") -> StrikesResponse:
        """
        Retrieve available strikes for a given underlying contract and month.
        
        Args:
            conid (str): Underlying contract ID.
            sectype (str): Security type (e.g., 'OPT').
            month (str): Contract month (e.g., 'OCT24').
            exchange (str): Listing exchange (default 'SMART').
            
        Returns:
            StrikesResponse: Validated list of call and put strikes.
        """
        self.logger.info(f"Fetching strikes for conid {conid}, month {month}")
        endpoint = "/iserver/secdef/strikes"
        params = {"conid": conid, "sectype": sectype, "month": month, "exchange": exchange}
        try:
            data = self.client.get(endpoint, params=params)
            response = StrikesResponse(**data)
            self.logger.log_action(
                "get_strikes",
                message=f"Retrieved strikes for conid {conid} month {month}.",
                details={"conid": conid, "month": month, "call_count": len(response.call)}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch strikes for {conid}: {e}")
            raise

    def get_trading_schedule(self, conid: str, exchange: Optional[str] = None) -> ContractTradingScheduleResponse:
        """
        Retrieve the trading schedule for a specific contract ID.
        
        Args:
            conid (str): The contract ID.
            exchange (Optional[str]): Target exchange.
            
        Returns:
            ContractTradingScheduleResponse: Validated trading schedule details.
        """
        self.logger.info(f"Fetching trading schedule for conid: {conid}")
        endpoint = "/contract/trading-schedule"
        params = {"conid": conid}
        if exchange is not None:
            params["exchange"] = exchange
        try:
            data = self.client.get(endpoint, params=params)
            response = ContractTradingScheduleResponse(**data)
            self.logger.log_action(
                "get_trading_schedule",
                message=f"Retrieved trading schedule for conid {conid}.",
                details={"conid": conid, "exchange": exchange}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch trading schedule for {conid}: {e}")
            raise

    def get_trading_schedule_by_symbol(self, symbol: str, sectype: str, exchange: Optional[str] = None) -> TradingScheduleResponse:
        """
        Retrieve the trading schedule by instrument symbol.
        
        Args:
            symbol (str): Instrument symbol.
            sectype (str): Security type (matches assetClass in query).
            exchange (Optional[str]): Target exchange.
            
        Returns:
            TradingScheduleResponse: Validated trading schedule details.
        """
        self.logger.info(f"Fetching trading schedule for symbol: {symbol} ({sectype})")
        endpoint = "/trsrv/secdef/schedule"
        params = {"symbol": symbol, "assetClass": sectype}
        if exchange is not None:
            params["exchange"] = exchange
        try:
            data = self.client.get(endpoint, params=params)
            if isinstance(data, dict):
                data = [data]
            response = TradingScheduleResponse(data)
            self.logger.log_action(
                "get_trading_schedule_by_symbol",
                message=f"Retrieved trading schedule for symbol {symbol}.",
                details={"symbol": symbol, "sectype": sectype, "exchange": exchange}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch trading schedule for symbol {symbol}: {e}")
            raise

    def search_contract_rules(self, conid: int, isBuy: bool = True, exchange: Optional[str] = None) -> ContractRulesResponse:
        """
        Search rules for a given contract.
        
        Args:
            conid (int): Contract ID.
            isBuy (bool): True for Buy side, False for Sell side.
            exchange (Optional[str]): Exchange.
            
        Returns:
            ContractRulesResponse: Validated contract rules response.
        """
        self.logger.info(f"Fetching contract rules for conid: {conid} (isBuy: {isBuy})")
        endpoint = "/iserver/contract/rules"
        payload = {"conid": conid, "isBuy": isBuy}
        if exchange is not None:
            payload["exchange"] = exchange
        try:
            data = self.client.post(endpoint, json_data=payload)
            response = ContractRulesResponse(**data) if isinstance(data, dict) else ContractRulesResponse(rules=data)
            self.logger.log_action(
                "search_contract_rules",
                message=f"Retrieved contract rules for conid {conid}.",
                details={"conid": conid, "isBuy": isBuy}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch contract rules for conid {conid}: {e}")
            raise

    def get_algos(self, conid: str, addDescription: Optional[str] = None, addParams: Optional[str] = None, algos: Optional[str] = None) -> AlgosResponse:
        """
        Retrieve available algo strategies for a contract.
        
        Args:
            conid (str): Contract ID.
            addDescription (Optional[str]): Set to "1" to include descriptions.
            addParams (Optional[str]): Set to "1" to show parameters.
            algos (Optional[str]): Semicolon-delimited list of specific algos to filter.
            
        Returns:
            AlgosResponse: Validated list of algos.
        """
        self.logger.info(f"Fetching algos for conid: {conid}")
        endpoint = f"/iserver/contract/{conid}/algos"
        params = {}
        if addDescription is not None:
            params["addDescription"] = addDescription
        if addParams is not None:
            params["addParams"] = addParams
        if algos is not None:
            params["algos"] = algos
        try:
            data = self.client.get(endpoint, params=params)
            response = AlgosResponse(**data)
            self.logger.log_action(
                "get_algos",
                message=f"Retrieved algos for conid {conid}.",
                details={"conid": conid}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch algos for conid {conid}: {e}")
            raise

    def get_instrument_info(self, conid: str) -> InstrumentInfoResponse:
        """
        Retrieve detailed contract info for a specific contract ID.
        
        Args:
            conid (str): The contract ID.
            
        Returns:
            InstrumentInfoResponse: Validated detailed contract info.
        """
        self.logger.info(f"Fetching instrument info for conid: {conid}")
        endpoint = f"/iserver/contract/{conid}/info"
        try:
            data = self.client.get(endpoint)
            response = InstrumentInfoResponse(**data)
            self.logger.log_action(
                "get_instrument_info",
                message=f"Retrieved instrument info for conid {conid}.",
                details={"conid": conid}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch instrument info for conid {conid}: {e}")
            raise

    def get_info_and_rules(self, conid: str) -> InfoAndRulesResponse:
        """
        Retrieve detailed contract info and rules for a specific contract ID.
        
        Args:
            conid (str): The contract ID.
            
        Returns:
            InfoAndRulesResponse: Validated detailed contract info and rules.
        """
        self.logger.info(f"Fetching info and rules for conid: {conid}")
        endpoint = f"/iserver/contract/{conid}/info-and-rules"
        try:
            data = self.client.get(endpoint)
            response = InfoAndRulesResponse(**data)
            self.logger.log_action(
                "get_info_and_rules",
                message=f"Retrieved info and rules for conid {conid}.",
                details={"conid": conid}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch info and rules for conid {conid}: {e}")
            raise

    def get_currency_pairs(self, currency: str) -> CurrencyPairsResponse:
        """
        Retrieve available currency pairs corresponding to a target currency.
        
        Args:
            currency (str): The target FX currency (e.g. 'USD').
            
        Returns:
            CurrencyPairsResponse: Validated list of currency pairs.
        """
        self.logger.info(f"Fetching currency pairs for currency: {currency}")
        endpoint = "/iserver/currency/pairs"
        params = {"currency": currency}
        try:
            data = self.client.get(endpoint, params=params)
            response = CurrencyPairsResponse(root=data)
            self.logger.log_action(
                "get_currency_pairs",
                message=f"Retrieved currency pairs for currency {currency}.",
                details={"currency": currency}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch currency pairs for currency {currency}: {e}")
            raise

    def get_exchange_rate(self, source: str, target: str) -> ExchangeRateResponse:
        """
        Retrieve currency exchange rate.
        
        Args:
            source (str): Base currency.
            target (str): Quote currency.
            
        Returns:
            ExchangeRateResponse: Validated currency exchange rate details.
        """
        self.logger.info(f"Fetching exchange rate from {source} to {target}")
        endpoint = "/iserver/exchangerate"
        params = {"source": source, "target": target}
        try:
            data = self.client.get(endpoint, params=params)
            payload = {**data}
            if "source" not in payload:
                payload["source"] = source
            if "target" not in payload:
                payload["target"] = target
            response = ExchangeRateResponse(**payload)
            self.logger.log_action(
                "get_exchange_rate",
                message=f"Retrieved exchange rate from {source} to {target}: {response.rate}",
                details={"source": source, "target": target, "rate": response.rate}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch exchange rate from {source} to {target}: {e}")
            raise

    def get_bond_filters(self, issuerId: str, symbol: str = "BOND") -> BondFiltersResponse:
        """
        Retrieve bond filters for an issuer.
        
        Args:
            issuerId (str): Issuer identifier.
            symbol (str): Symbol (default 'BOND').
            
        Returns:
            BondFiltersResponse: Validated bond filters details.
        """
        self.logger.info(f"Fetching bond filters for issuerId: {issuerId}")
        endpoint = "/iserver/secdef/bond-filters"
        params = {"symbol": symbol, "issuerId": issuerId}
        try:
            data = self.client.get(endpoint, params=params)
            response = BondFiltersResponse(**data)
            self.logger.log_action(
                "get_bond_filters",
                message=f"Retrieved bond filters for issuerId {issuerId}.",
                details={"issuerId": issuerId}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch bond filters for issuerId {issuerId}: {e}")
            raise

    def get_all_conids_by_exchange(self, exchange: str) -> AllConidsResponse:
        """
        Retrieve all tradable stock conids on a specified exchange.
        
        Args:
            exchange (str): Exchange name.
            
        Returns:
            AllConidsResponse: Validated list of conids.
        """
        self.logger.info(f"Fetching all conids for exchange: {exchange}")
        endpoint = "/trsrv/all-conids"
        params = {"exchange": exchange}
        try:
            data = self.client.get(endpoint, params=params)
            response = AllConidsResponse(data)
            self.logger.log_action(
                "get_all_conids_by_exchange",
                message=f"Retrieved {len(response.root)} conids for exchange {exchange}.",
                details={"exchange": exchange, "count": len(response.root)}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch all conids for exchange {exchange}: {e}")
            raise

    def search_futures_by_symbol(self, symbols: str) -> FuturesResponse:
        """
        Retrieve non-expired future contracts for a given comma-separated symbol list.
        
        Args:
            symbols (str): Comma-delimited ticker symbols.
            
        Returns:
            FuturesResponse: Validated mapping of symbol to list of futures.
        """
        self.logger.info(f"Fetching futures for symbols: {symbols}")
        endpoint = "/trsrv/futures"
        params = {"symbols": symbols}
        try:
            data = self.client.get(endpoint, params=params)
            response = FuturesResponse(data)
            self.logger.log_action(
                "search_futures_by_symbol",
                message=f"Retrieved futures for symbols {symbols}.",
                details={"symbols": symbols}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch futures for symbols {symbols}: {e}")
            raise

    def get_instrument_definition(self, conids: str) -> TrsrvSecdefResponse:
        """
        Retrieve security definitions for a specified list of comma-separated contract IDs.
        
        Args:
            conids (str): Comma-delimited contract IDs.
            
        Returns:
            TrsrvSecdefResponse: Validated list of security definitions.
        """
        self.logger.info(f"Fetching security definitions for conids: {conids}")
        endpoint = "/trsrv/secdef"
        params = {"conids": conids}
        try:
            data = self.client.get(endpoint, params=params)
            response = TrsrvSecdefResponse(**data)
            self.logger.log_action(
                "get_instrument_definition",
                message=f"Retrieved instrument definitions for conids {conids}.",
                details={"conids": conids}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch instrument definitions for conids {conids}: {e}")
            raise

    def search_stocks_by_symbol(self, symbols: str) -> StocksResponse:
        """
        Resolve stock symbols into contract info.
        
        Args:
            symbols (str): Comma-delimited list of capitalized stock symbols.
            
        Returns:
            StocksResponse: Validated mapping of stock symbol to stock contracts.
        """
        self.logger.info(f"Fetching stocks for symbols: {symbols}")
        endpoint = "/trsrv/stocks"
        params = {"symbols": symbols}
        try:
            data = self.client.get(endpoint, params=params)
            response = StocksResponse(data)
            self.logger.log_action(
                "search_stocks_by_symbol",
                message=f"Retrieved stocks for symbols {symbols}.",
                details={"symbols": symbols}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch stocks for symbols {symbols}: {e}")
            raise

    def get_forecast_categories(self) -> ForecastCategoryTreeResponse:
        """
        Retrieve all Event Contract Forecast categories and underlying markets.
        
        Returns:
            ForecastCategoryTreeResponse: Validated forecast categories tree.
        """
        self.logger.info("Fetching forecast category tree")
        endpoint = "/forecast/category/tree"
        try:
            data = self.client.get(endpoint)
            # Make sure we wrap dict into categories if returned as top-level dict
            if isinstance(data, dict) and "categories" not in data:
                data = {"categories": data}
            response = ForecastCategoryTreeResponse(**data)
            self.logger.log_action(
                "get_forecast_categories",
                message="Retrieved forecast category tree.",
                details={"category_count": len(response.categories) if response.categories else 0}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch forecast category tree: {e}")
            raise

    def get_forecast_contract_details(self, conid: int) -> ForecastContractDetail:
        """
        Retrieve detailed attributes for a specific forecast contract.
        
        Args:
            conid (int): The contract outcome ID.
            
        Returns:
            ForecastContractDetail: Validated detailed contract info.
        """
        self.logger.info(f"Fetching forecast contract details for conid: {conid}")
        endpoint = "/forecast/contract/details"
        params = {"conid": conid}
        try:
            data = self.client.get(endpoint, params=params)
            response = ForecastContractDetail(**data)
            self.logger.log_action(
                "get_forecast_contract_details",
                message=f"Retrieved forecast contract details for conid {conid}.",
                details={"conid": conid, "symbol": response.symbol}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch forecast contract details for conid {conid}: {e}")
            raise

    def get_forecast_market(self, underlyingConid: int) -> ForecastMarketResponse:
        """
        Retrieve all contracts for a given underlying market ConID.
        
        Args:
            underlyingConid (int): The underlying market ConID.
            
        Returns:
            ForecastMarketResponse: Validated underlying market contracts.
        """
        self.logger.info(f"Fetching forecast market contracts for underlying conid: {underlyingConid}")
        endpoint = "/forecast/contract/market"
        params = {"underlyingConid": underlyingConid}
        try:
            data = self.client.get(endpoint, params=params)
            response = ForecastMarketResponse(**data)
            self.logger.log_action(
                "get_forecast_market",
                message=f"Retrieved forecast market contracts for underlying conid {underlyingConid}.",
                details={"underlyingConid": underlyingConid, "contract_count": len(response.contracts) if response.contracts else 0}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch forecast market contracts for underlying conid {underlyingConid}: {e}")
            raise

    def get_forecast_rules(self, conid: int) -> ForecastRulesResponse:
        """
        Retrieve trading terms and rules for a forecast contract.
        
        Args:
            conid (int): The contract outcome ID.
            
        Returns:
            ForecastRulesResponse: Validated forecast contract rules.
        """
        self.logger.info(f"Fetching forecast rules for conid: {conid}")
        endpoint = "/forecast/contract/rules"
        params = {"conid": conid}
        try:
            data = self.client.get(endpoint, params=params)
            response = ForecastRulesResponse(**data)
            self.logger.log_action(
                "get_forecast_rules",
                message=f"Retrieved forecast rules for conid {conid}.",
                details={"conid": conid}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch forecast rules for conid {conid}: {e}")
            raise

    def get_forecast_schedules(self, conid: int) -> ForecastSchedulesResponse:
        """
        Retrieve trading schedules for a forecast contract.
        
        Args:
            conid (int): The contract outcome ID.
            
        Returns:
            ForecastSchedulesResponse: Validated trading schedules.
        """
        self.logger.info(f"Fetching forecast schedules for conid: {conid}")
        endpoint = "/forecast/contract/schedules"
        params = {"conid": conid}
        try:
            data = self.client.get(endpoint, params=params)
            response = ForecastSchedulesResponse(**data)
            self.logger.log_action(
                "get_forecast_schedules",
                message=f"Retrieved forecast schedules for conid {conid}.",
                details={"conid": conid}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch forecast schedules for conid {conid}: {e}")
            raise
