"""
Core logic for the IBKR Watchlist tool.
This module provides the WatchlistManager class to interact with IBKR watchlist endpoints.
"""
from typing import List, Dict, Any, Optional
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..schemas.watchlist_schemas import (
    WatchlistsResponse,
    WatchlistDetail,
    WatchlistRow,
    WatchlistRequest
)

class WatchlistManager:
    """
    Manager for IBKR Watchlist operations.
    
    This class wraps the /iserver/watchlists and /iserver/watchlist endpoints,
    ensuring all actions are logged and validated.
    """
    def __init__(self):
        """
        Initialize the WatchlistManager.
        """
        self.tool_name = "watchlist"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def list_watchlists(self) -> WatchlistsResponse:
        """
        Retrieve all available watchlists (User-defined, System, and All).
        
        Returns:
            WatchlistsResponse: Validated grouped watchlists.
        """
        self.logger.debug("Listing all available watchlists.")
        endpoint = "/iserver/watchlists"
        try:
            data = self.client.get(endpoint)
            response = WatchlistsResponse(**data)
            self.logger.log_action("list_watchlists", level="DEBUG", message="Retrieved watchlist list.")
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch watchlist list: {e}")
            raise

    def get_watchlist(self, watchlist_id: str) -> WatchlistDetail:
        """
        Retrieve the contents of a specific watchlist by its ID.
        
        Args:
            watchlist_id (str): The unique identifier for the watchlist.
            
        Returns:
            WatchlistDetail: Validated detail of the specific watchlist.
        """
        self.logger.debug(f"Fetching detail for watchlist ID: {watchlist_id}")
        endpoint = "/iserver/watchlist"
        params = {"id": watchlist_id}
        try:
            data = self.client.get(endpoint, params=params)
            # Filter out empty rows or spacers as requested
            if "rows" in data:
                data["rows"] = [row for row in data["rows"] if row.get("conid")]
            
            response = WatchlistDetail(**data)
            self.logger.log_action(
                "get_watchlist", 
                level="DEBUG",
                message=f"Retrieved detail for watchlist {watchlist_id} ({response.name})."
            )
            return response
        except Exception as e:
            self.logger.error(f"Failed to fetch watchlist {watchlist_id}: {e}")
            raise

    def create_watchlist(self, name: str, conids: List[int]) -> Optional[Dict[str, Any]]:
        """
        Create a new user-defined watchlist.
        
        Args:
            name (str): The name for the new watchlist.
            conids (List[int]): List of contract IDs to include.
            
        Returns:
            Optional[Dict[str, Any]]: API response if successful.
        """
        self.logger.info(f"Creating new watchlist: {name}")
        endpoint = "/iserver/watchlist"
        rows = [WatchlistRow(conid=cid) for cid in conids]
        payload = WatchlistRequest(name=name, rows=rows)
        
        try:
            data = self.client.post(endpoint, json_data=payload.model_dump(by_alias=True))
            self.logger.log_action(
                "create_watchlist", 
                message=f"Created watchlist '{name}' with {len(conids)} contracts.",
                details={"name": name, "conids": conids}
            )
            return data
        except Exception as e:
            self.logger.error(f"Failed to create watchlist '{name}': {e}")
            raise

    def delete_watchlist(self, watchlist_id: str) -> Optional[Dict[str, Any]]:
        """
        Delete a user-defined watchlist.
        
        Args:
            watchlist_id (str): The ID of the watchlist to delete.
            
        Returns:
            Optional[Dict[str, Any]]: API response if successful.
        """
        self.logger.info(f"Deleting watchlist: {watchlist_id}")
        endpoint = "/iserver/watchlist"
        params = {"id": watchlist_id}
        try:
            data = self.client.delete(endpoint, json_data={"id": watchlist_id})
            # Note: client.delete in common/api_client handles query params via kwargs if needed,
            # but usually IBKR /iserver/watchlist DELETE expects the ID in query or body.
            # I will use query param as it's common for DELETE here.
            # Re-checking _request in api_client: it takes params.
            data = self.client.delete(f"{endpoint}?id={watchlist_id}")
            
            self.logger.log_action("delete_watchlist", message=f"Deleted watchlist {watchlist_id}.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to delete watchlist {watchlist_id}: {e}")
            raise

    def add_to_watchlist(self, watchlist_id: str, conids: List[int]) -> Optional[Dict[str, Any]]:
        """
        Add contracts to an existing watchlist using a fetch-modify-update pattern.
        """
        self.logger.info(f"Adding {len(conids)} contracts to watchlist {watchlist_id}")
        current = self.get_watchlist(watchlist_id)
        
        # Merge existing conids with new ones, avoiding duplicates
        existing_conids = {row.conid for row in current.rows if row.conid}
        new_conids = list(existing_conids)
        for cid in conids:
            if cid not in existing_conids:
                new_conids.append(cid)
        
        rows = [WatchlistRow(conid=cid) for cid in new_conids]
        payload = WatchlistRequest(name=current.name, rows=rows)
        
        endpoint = f"/iserver/watchlist?id={watchlist_id}"
        try:
            data = self.client.post(endpoint, json_data=payload.model_dump(by_alias=True))
            self.logger.log_action(
                "add_to_watchlist", 
                message=f"Added contracts to {watchlist_id}.",
                details={"id": watchlist_id, "added": conids}
            )
            return data
        except Exception as e:
            self.logger.error(f"Failed to add to watchlist {watchlist_id}: {e}")
            raise

    def remove_from_watchlist(self, watchlist_id: str, conids: List[int]) -> Optional[Dict[str, Any]]:
        """
        Remove contracts from an existing watchlist using a fetch-modify-update pattern.
        """
        self.logger.info(f"Removing {len(conids)} contracts from watchlist {watchlist_id}")
        current = self.get_watchlist(watchlist_id)
        
        to_remove = set(conids)
        new_conids = [row.conid for row in current.rows if row.conid and row.conid not in to_remove]
        
        rows = [WatchlistRow(conid=cid) for cid in new_conids]
        payload = WatchlistRequest(name=current.name, rows=rows)
        
        endpoint = f"/iserver/watchlist?id={watchlist_id}"
        try:
            data = self.client.post(endpoint, json_data=payload.model_dump(by_alias=True))
            self.logger.log_action(
                "remove_from_watchlist", 
                message=f"Removed contracts from {watchlist_id}.",
                details={"id": watchlist_id, "removed": conids}
            )
            return data
        except Exception as e:
            self.logger.error(f"Failed to remove from watchlist {watchlist_id}: {e}")
            raise
