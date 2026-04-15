"""
API Client for interacting with the IBKR Client Portal Gateway.
This module handles communication with the local IBKR API gateway,
including session management, authentication status checks, and request pacing.
"""
import requests
import urllib3
import time
from typing import Any, Dict, Optional, Union
from .config import get_ibkr_config
from .logger import IBKRLogger

# Disable insecure request warnings for local gateway as it typically uses self-signed certs.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IBKRClient:
    """
    Client for the IBKR Web API (Client Portal API).
    
    This class manages an HTTP session and provides helper methods to interact
    with the various /iserver endpoints, ensuring the session is authenticated.
    """
    def __init__(self, tool_name: str):
        """
        Initialize the API client from configuration.

        Args:
            tool_name (str): Name of the tool using this client (for logging).
        """
        self.config = get_ibkr_config()["api"]
        self.base_url = self.config["base_url"].rstrip("/")
        self.verify_ssl = self.config.get("verify_ssl", False)
        self.timeout = self.config.get("timeout_seconds", 30)
        self.logger = IBKRLogger(tool_name)
        
        # Initialize the session and common headers
        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        self.session.headers.update({
            "User-Agent": "Console",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP request with error handling and pacing management.

        Pacing is critical for the IBKR API (10 requests per second limit).
        IP addresses can be blocked for 15 minutes if limits are exceeded.

        Args:
            method (str): HTTP method (GET, POST, DELETE, etc.).
            endpoint (str): API endpoint path.
            **kwargs: Additional arguments for requests.request.

        Returns:
            requests.Response: The HTTP response object.

        Raises:
            requests.exceptions.HTTPError: For non-2xx status codes.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Explicit pacing: ensure we don't exceed 10 requests per second.
        # Sleeping for ~120ms between requests keeps us safely below the limit.
        time.sleep(0.12)
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            
            # Handle specifically the 'Too Many Requests' error.
            if response.status_code == 429:
                self.logger.error("Pacing limit exceeded (429) on IBKR Gateway.")
            
            # Raise an error for 4xx or 5xx responses.
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {method} {endpoint} - {e}")
            raise

    def check_auth_status(self) -> bool:
        """
        Determine if the current brokerage session is fully authenticated.
        If the session is connected but not authenticated, it attempts to 
        initialize the brokerage session automatically.

        Returns:
            bool: True if fully authenticated, False otherwise.
        """
        try:
            response = self._request("GET", "/iserver/auth/status")
            status = response.json()
            authenticated = status.get("authenticated", False)
            connected = status.get("connected", False)
            
            # Tiered session check: if connected but not trading-enabled, initialize.
            if not authenticated and connected:
                self.logger.info("Session connected but not authenticated. Initializing...")
                self.initialize_brokerage_session()
                # Re-check status after initialization attempt
                return self.check_auth_status()
            
            return authenticated
        except Exception as e:
            self.logger.error(f"Failed to check authentication status: {e}")
            return False

    def initialize_brokerage_session(self):
        """
        Request initialization of the brokerage session via the Gateway.
        This is required for all /iserver endpoints that need trading permissions.
        """
        try:
            self._request("POST", "/iserver/auth/ssodh/init")
            self.logger.info("Brokerage session initialization command sent to Gateway.")
        except Exception as e:
            self.logger.error(f"Failed to initialize brokerage session: {e}")
            raise

    def tickle(self):
        """
        Call the /tickle endpoint to prevent the session from timing out.
        Brokerage sessions time out after 5 minutes of inactivity.
        """
        try:
            self._request("POST", "/tickle")
            self.logger.debug("Sent tickle to keep session alive.")
        except Exception as e:
            self.logger.error(f"Tickle request failed: {e}")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Union[Dict, Any]:
        """
        Perform a GET request and return the JSON response.
        
        Args:
            endpoint (str): The API endpoint.
            params (Optional[Dict]): Query parameters.

        Returns:
            Union[Dict, Any]: The parsed JSON response body.
        """
        response = self._request("GET", endpoint, params=params)
        return response.json()

    def post(self, endpoint: str, json_data: Optional[Dict] = None) -> Union[Dict, Any]:
        """
        Perform a POST request and return the JSON response.

        Args:
            endpoint (str): The API endpoint.
            json_data (Optional[Dict]): The request body as a dictionary.

        Returns:
            Union[Dict, Any]: The parsed JSON response body.
        """
        response = self._request("POST", endpoint, json=json_data)
        return response.json()

    def delete(self, endpoint: str, json_data: Optional[Dict] = None) -> Union[Dict, Any]:
        """
        Perform a DELETE request and return the JSON response.

        Args:
            endpoint (str): The API endpoint.
            json_data (Optional[Dict]): The request body as a dictionary.

        Returns:
            Union[Dict, Any]: The parsed JSON response body.
        """
        response = self._request("DELETE", endpoint, json=json_data)
        return response.json()
