"""
Core logic for the IBKR Market Data tool.
This module provides the MarketDataManager class to interact with IBKR market data endpoints,
specifically supporting historical OHLCV bar data retrieval.
"""
from typing import Optional
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..schemas.marketdata_schemas import HistoricalDataResponse

class MarketDataManager:
    """
    Manager for IBKR market data-related operations.
    
    This class wraps the /iserver/marketdata endpoints, ensuring all queries
    are logged, pacing-compliant, and schema-validated.
    """
    def __init__(self):
        """
        Initialize the MarketDataManager.
        
        Sets up the API client and the dual-logging system.
        """
        self.tool_name = "marketdata"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def get_historical_data(
        self,
        conid: int,
        period: str,
        bar: str,
        outsideRth: Optional[bool] = None,
        barType: Optional[str] = None,
        startTime: Optional[str] = None
    ) -> HistoricalDataResponse:
        """
        Retrieve historical bar data (OHLCV) for a specific contract ID.

        Args:
            conid (int): The unique contract identifier.
            period (str): The duration of the historical data to retrieve (e.g., '1d', '1w').
            bar (str): The bar size / interval (e.g., '1min', '5min', '1h', '1d').
            outsideRth (Optional[bool]): If True, include data outside of regular trading hours.
            barType (Optional[str]): The type of bar data (e.g., 'last', 'midprice', 'bid', 'ask').
            startTime (Optional[str]): Start date/time in 'YYYYMMDD-hh:mm:ss' format.

        Returns:
            HistoricalDataResponse: Validated historical bar data response.
        """
        self.logger.info(f"Fetching historical market data for conid: {conid} (period: {period}, bar: {bar})")
        endpoint = "/iserver/marketdata/history"
        params = {
            "conid": str(conid),
            "period": period,
            "bar": bar
        }
        
        if outsideRth is not None:
            params["outsideRth"] = "true" if outsideRth else "false"
        if barType is not None:
            params["barType"] = barType
        if startTime is not None:
            params["startTime"] = startTime

        try:
            data = self.client.get(endpoint, params=params)
            response = HistoricalDataResponse(**data)
            
            self.logger.log_action(
                action="get_historical_data",
                message=f"Retrieved {len(response.data)} historical bars for conid {conid}.",
                details={
                    "conid": conid,
                    "period": period,
                    "bar": bar,
                    "outsideRth": outsideRth,
                    "barType": barType,
                    "startTime": startTime,
                    "bar_count": len(response.data)
                }
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to retrieve historical data for conid {conid}: {e}")
            raise
