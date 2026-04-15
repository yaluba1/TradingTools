"""
Core logic for the IBKR Scanner tool.
This module provides the ScannerManager class to interact with IBKR scanner endpoints.
"""
from typing import List, Dict, Any, Optional
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..schemas.scanner_schemas import (
    ScannerParams,
    ScannerRequest,
    ScannerResponse,
    ScannerFilter
)

class ScannerManager:
    """
    Manager for IBKR Market Scanner operations.
    
    This class wraps the /iserver/scanner/params and /iserver/scanner/run endpoints.
    Note: /scanner/params has a strict 1 request per 15 minutes limit.
    """
    def __init__(self):
        """
        Initialize the ScannerManager.
        """
        self.tool_name = "scanner"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def get_params(self) -> ScannerParams:
        """
        Retrieve available scanner parameters from the Gateway.
        
        Note: This endpoint should not be called more than once every 15 minutes.
        
        Returns:
            ScannerParams: Validated scanner parameters.
        """
        self.logger.info("Fetching available scanner parameters (15-min rate limit applies).")
        endpoint = "/iserver/scanner/params"
        try:
            data = self.client.get(endpoint)
            params = ScannerParams(**data)
            self.logger.log_action("get_params", level="DEBUG", message="Retrieved scanner parameters successfully.")
            return params
        except Exception as e:
            self.logger.error(f"Failed to fetch scanner parameters: {e}")
            raise

    def run_scan(
        self, 
        instrument: str, 
        scan_type: str, 
        location: str, 
        filters: Optional[List[Dict[str, Any]]] = None
    ) -> ScannerResponse:
        """
        Execute a market scan based on the provided criteria.

        Args:
            instrument (str): The asset class (e.g., STK, FUT).
            scan_type (str): The scanner parameter code (e.g., MOST_ACTIVE).
            location (str): Geographical/exchange code (e.g., STK.US.MAJOR).
            filters (Optional[List[Dict[str, Any]]]): List of filter objects.

        Returns:
            ScannerResponse: Validated scan results.
        """
        self.logger.info(f"Executing scan: {scan_type} on {instrument} in {location}")
        endpoint = "/iserver/scanner/run"
        
        # Construct the request payload
        scan_filters = []
        if filters:
            scan_filters = [ScannerFilter(**f) for f in filters]
            
        payload = ScannerRequest(
            instrument=instrument,
            type=scan_type,
            location=location,
            filter=scan_filters
        )

        try:
            data = self.client.post(endpoint, json_data=payload.model_dump())
            
            # The API often returns a list directly or an object with 'results'
            # Adjust mapping if needed based on typical CPAPI responses.
            if isinstance(data, list):
                # Ensure we format it correctly for the schema if it's just a raw list
                formatted_data = {
                    "total": len(data),
                    "offset": 0,
                    "limit": len(data),
                    "results": data
                }
            else:
                formatted_data = data

            response = ScannerResponse(**formatted_data)
            self.logger.log_action(
                "run_scan", 
                level="DEBUG",
                message=f"Scan executed successfully. Found {len(response.results)} results."
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to execute scan: {e}")
            raise
