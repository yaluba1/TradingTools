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
    TradingScheduleResponse
)

class ContractManager:
    """
    Manager for IBKR contract-related operations.
    
    This class wraps the /iserver/secdef endpoints, ensuring all searches 
    and details retrieval are logged and validated.
    """
    def __init__(self):
        """
        Initialize the ContractManager.
        
        Sets up the API client with pacing support and the logger for file recording.
        """
        self.tool_name = "contract"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def search_contracts(self, symbol: str) -> ContractSearchResponse:
        """
        Search for a security definition by symbol.
        
        Args:
            symbol (str): The ticker symbol to search for (e.g., 'AAPL').
            
        Returns:
            ContractSearchResponse: Validated list of matching contracts.
        """
        self.logger.info(f"Searching for contracts with symbol: {symbol}")
        endpoint = "/iserver/secdef/search"
        payload = {"symbol": symbol}
        try:
            # The search endpoint is a POST request taking a JSON body with symbol.
            data = self.client.post(endpoint, json_data=payload)
            # Response is typically a list of dicts.
            response = ContractSearchResponse(data)
            self.logger.log_action(
                "search_contracts",
                message=f"Found {len(response.root)} results for {symbol}.",
                details={"symbol": symbol, "count": len(response.root)}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to search contracts for {symbol}: {e}")
            raise

    def get_contract_details(self, conid: str, sec_type: str = "STK") -> ContractInfoResponse:
        """
        Retrieve detailed information and rules for a specific contract.
        
        Args:
            conid (str): The contract ID.
            sec_type (str): The security type (default 'STK').
            
        Returns:
            ContractInfoResponse: Validated detailed contract info.
        """
        self.logger.info(f"Fetching details for conid: {conid} (Type: {sec_type})")
        endpoint = "/iserver/secdef/info"
        params = {"conid": conid, "sectype": sec_type}
        try:
            data = self.client.get(endpoint, params=params)
            response = ContractInfoResponse(data)
            self.logger.log_action(
                "get_contract_details",
                message=f"Retrieved info for conid {conid}.",
                details={"conid": conid, "secType": sec_type}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch contract details for {conid}: {e}")
            raise

    def get_strikes(self, conid: str, sec_type: str, month: str, exchange: str = "SMART") -> StrikesResponse:
        """
        Retrieve available strikes for a given underlying contract and month.
        
        Args:
            conid (str): Underlying contract ID.
            sec_type (str): Security type (e.g., 'OPT').
            month (str): Contract month (e.g., 'OCT24').
            exchange (str): Listing exchange (default 'SMART').
            
        Returns:
            StrikesResponse: Validated list of call and put strikes.
        """
        self.logger.info(f"Fetching strikes for conid {conid}, month {month}")
        endpoint = "/iserver/secdef/strikes"
        params = {"conid": conid, "sectype": sec_type, "month": month, "exchange": exchange}
        try:
            # Note: /iserver/secdef/search must be called for the underlying conid first
            # to prime the gateway's cache, as per IBKR documentation.
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

    def get_trading_schedule(self, conid: str) -> TradingScheduleResponse:
        """
        Retrieve the trading schedule for a specific instrument.
        
        Args:
            conid (str): The contract ID.
            
        Returns:
            TradingScheduleResponse: Validated list of trading sessions.
        """
        self.logger.info(f"Fetching trading schedule for conid: {conid}")
        endpoint = "/iserver/secdef/tradingschedule"
        params = {"conid": conid}
        try:
            data = self.client.get(endpoint, params=params)
            response = TradingScheduleResponse(data)
            self.logger.log_action(
                "get_trading_schedule",
                message=f"Retrieved trading schedule for conid {conid}.",
                details={"conid": conid}
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch trading schedule for {conid}: {e}")
            raise
