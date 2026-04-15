"""
Core logic for the IBKR Portfolio tool.
This module provides the PortfolioManager class to interact with IBKR portfolio
and Portfolio Analyst (PA) endpoints.
"""
from typing import List, Dict, Any, Optional, Union
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..schemas.portfolio_schemas import (
    PortfolioAccountsResponse,
    PortfolioPositionsResponse,
    PortfolioLedgerResponse,
    PortfolioSummaryResponse,
    PortfolioAllocationResponse,
    PAPerformanceResponse,
    PASummaryResponse,
    PATransactionsResponse
)

class PortfolioManager:
    """
    Manager for IBKR Portfolio and Portfolio Analyst operations.
    
    This class wraps /portfolio and /pa endpoints, ensuring responses
    are validated against Pydantic schemas and actions are logged appropriately.
    """
    def __init__(self):
        """
        Initialize the PortfolioManager.
        """
        self.tool_name = "portfolio"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def list_accounts(self) -> PortfolioAccountsResponse:
        """
        Retrieve a list of accounts associated with the portfolio.
        
        Returns:
            PortfolioAccountsResponse: Validated list of accounts.
        """
        self.logger.info("Fetching portfolio accounts.")
        endpoint = "/portfolio/accounts"
        try:
            data = self.client.get(endpoint)
            # Response is a list of account objects
            accounts = PortfolioAccountsResponse(accounts=data)
            self.logger.log_action(
                "list_accounts",
                message=f"Retrieved {len(accounts.accounts)} portfolio accounts."
            )
            return accounts
        except Exception as e:
            self.logger.error(f"Failed to fetch portfolio accounts: {e}")
            raise

    def get_summary(self, account_id: str) -> PortfolioSummaryResponse:
        """
        Retrieve portfolio summary characteristics for a specific account.
        
        Args:
            account_id (str): The account ID.
            
        Returns:
            PortfolioSummaryResponse: Validated summary data.
        """
        self.logger.info(f"Fetching portfolio summary for account: {account_id}")
        endpoint = f"/portfolio/{account_id}/summary"
        try:
            data = self.client.get(endpoint)
            # Response is a object with 'accountsummaries' list
            summary = PortfolioSummaryResponse(summary=data.get("accountsummaries", []))
            self.logger.log_action(
                "get_summary",
                account_id=account_id,
                message=f"Retrieved portfolio summary for {account_id}."
            )
            return summary
        except Exception as e:
            self.logger.error(f"Failed to fetch portfolio summary for {account_id}: {e}")
            raise

    def get_ledger(self, account_id: str) -> PortfolioLedgerResponse:
        """
        Retrieve portfolio ledger (balances) for a specific account.
        
        Args:
            account_id (str): The account ID.
            
        Returns:
            PortfolioLedgerResponse: Validated ledger data.
        """
        self.logger.info(f"Fetching ledger for account: {account_id}")
        endpoint = f"/portfolio/{account_id}/ledger"
        try:
            data = self.client.get(endpoint)
            # Response is a dict of currency structures
            ledger = PortfolioLedgerResponse(ledger=data)
            self.logger.log_action(
                "get_ledger",
                account_id=account_id,
                message=f"Retrieved ledger for {account_id}."
            )
            return ledger
        except Exception as e:
            self.logger.error(f"Failed to fetch ledger for {account_id}: {e}")
            raise

    def get_positions(self, account_id: str, page_id: int = 0) -> PortfolioPositionsResponse:
        """
        Retrieve portfolio positions for a specific account.
        
        Args:
            account_id (str): The account ID.
            page_id (int): Page number for pagination.
            
        Returns:
            PortfolioPositionsResponse: Validated list of positions.
        """
        self.logger.info(f"Fetching positions for account: {account_id}, page: {page_id}")
        endpoint = f"/portfolio/{account_id}/positions/{page_id}"
        try:
            data = self.client.get(endpoint)
            # Response is a list of position objects
            positions = PortfolioPositionsResponse(positions=data)
            self.logger.log_action(
                "get_positions",
                account_id=account_id,
                message=f"Retrieved {len(positions.positions)} positions for {account_id} (Page {page_id})."
            )
            return positions
        except Exception as e:
            self.logger.error(f"Failed to fetch positions for {account_id}: {e}")
            raise

    def invalidate_positions(self) -> Dict[str, Any]:
        """
        Invalidate the backend cache for portfolio positions.
        
        Returns:
            Dict[str, Any]: API response metadata.
        """
        self.logger.info("Invalidating portfolio positions cache.")
        endpoint = "/portfolio/positions/invalidate"
        try:
            data = self.client.post(endpoint)
            self.logger.log_action("invalidate_positions", message="Positions cache invalidated.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to invalidate positions cache: {e}")
            raise

    def get_allocation(self, account_id: Optional[str] = None) -> PortfolioAllocationResponse:
        """
        Retrieve portfolio allocation data.
        
        Args:
            account_id (Optional[str]): Account ID. If None, retrieves for all accounts.
            
        Returns:
            PortfolioAllocationResponse: Validated allocation data.
        """
        if account_id:
            self.logger.info(f"Fetching allocation for account: {account_id}")
            endpoint = f"/portfolio/{account_id}/allocation"
        else:
            self.logger.info("Fetching allocation for all accounts.")
            endpoint = "/portfolio/allocation"
            
        try:
            data = self.client.get(endpoint)
            allocation = PortfolioAllocationResponse(**data)
            self.logger.log_action(
                "get_allocation",
                account_id=account_id or "ALL",
                message=f"Retrieved allocation data for {account_id or 'all accounts'}."
            )
            return allocation
        except Exception as e:
            self.logger.error(f"Failed to fetch allocation: {e}")
            raise

    def get_performance(self, account_ids: List[str], freq: str = "D") -> PAPerformanceResponse:
        """
        Retrieve performance data from Portfolio Analyst.
        
        Args:
            account_ids (List[str]): List of account IDs.
            freq (str): Frequency of data ('D' daily, 'M' monthly, 'Q' quarterly, 'Y' yearly).
            
        Returns:
            PAPerformanceResponse: Validated performance data.
        """
        self.logger.info(f"Fetching PA performance for accounts: {account_ids}, freq: {freq}")
        endpoint = "/pa/performance"
        payload = {"acctIds": account_ids, "freq": freq}
        try:
            data = self.client.post(endpoint, json_data=payload)
            performance = PAPerformanceResponse(**data)
            self.logger.log_action(
                "get_performance",
                message=f"Retrieved performance for {len(account_ids)} accounts.",
                details={"acctIds": account_ids, "freq": freq}
            )
            return performance
        except Exception as e:
            self.logger.error(f"Failed to fetch PA performance: {e}")
            raise

    def get_pa_summary(self, account_ids: List[str]) -> PASummaryResponse:
        """
        Retrieve summary data from Portfolio Analyst.
        
        Args:
            account_ids (List[str]): List of account IDs.
            
        Returns:
            PASummaryResponse: Validated summary data.
        """
        self.logger.info(f"Fetching PA summary for accounts: {account_ids}")
        endpoint = "/pa/summary"
        payload = {"acctIds": account_ids}
        try:
            data = self.client.post(endpoint, json_data=payload)
            summary = PASummaryResponse(**data)
            self.logger.log_action(
                "get_pa_summary",
                message=f"Retrieved PA summary for {len(account_ids)} accounts.",
                details={"acctIds": account_ids}
            )
            return summary
        except Exception as e:
            self.logger.error(f"Failed to fetch PA summary: {e}")
            raise

    def get_transactions(self, account_ids: List[str], conid: Optional[int] = None, 
                         days: Optional[int] = None) -> PATransactionsResponse:
        """
        Retrieve historical transactions from Portfolio Analyst.
        
        Args:
            account_ids (List[str]): List of account IDs.
            conid (Optional[int]): Filter by contract ID.
            days (Optional[int]): Number of days to look back.
            
        Returns:
            PATransactionsResponse: Validated list of transactions.
        """
        self.logger.info(f"Fetching PA transactions for accounts: {account_ids}")
        endpoint = "/pa/transactions"
        payload = {"acctIds": account_ids}
        if conid:
            payload["conid"] = conid
        if days:
            payload["days"] = days
            
        try:
            data = self.client.post(endpoint, json_data=payload)
            # Response is typically a dictionary containing a list or just the list
            if isinstance(data, list):
                transactions = PATransactionsResponse(transactions=data)
            else:
                # Some implementations wrap it in a 'transactions' key
                transactions = PATransactionsResponse(transactions=data.get("transactions", []))
                
            self.logger.log_action(
                "get_transactions",
                message=f"Retrieved PA transactions for {len(account_ids)} accounts.",
                details=payload
            )
            return transactions
        except Exception as e:
            self.logger.error(f"Failed to fetch PA transactions: {e}")
            raise
