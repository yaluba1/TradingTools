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
    PortfolioSubaccountsResponse,
    PortfolioAccountMetaResponse,
    PortfolioPositionsResponse,
    PortfolioPositionsConidResponse,
    PortfolioPositionResponse,
    PortfolioLedgerResponse,
    PortfolioSummaryResponse,
    PortfolioAllocationResponse,
    PAPerformanceResponse,
    PASummaryResponse,
    PAAllocationResponse,
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
            # Response is a dictionary of summary characteristics
            summary = PortfolioSummaryResponse(summary=data)
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

    def get_positions(self, account_id: str, page_id: Optional[int] = None) -> PortfolioPositionsResponse:
        """
        Retrieve portfolio positions for a specific account.
        
        Args:
            account_id (str): The account ID.
            page_id (Optional[int]): Page number for pagination. If None, queries all positions.
            
        Returns:
            PortfolioPositionsResponse: Validated list of positions.
        """
        if page_id is not None:
            self.logger.info(f"Fetching positions for account: {account_id}, page: {page_id}")
            endpoint = f"/portfolio/{account_id}/positions/{page_id}"
        else:
            self.logger.info(f"Fetching positions for account: {account_id}")
            endpoint = f"/portfolio/{account_id}/positions"
            
        try:
            data = self.client.get(endpoint)
            # Response is a list of position objects
            positions = PortfolioPositionsResponse(positions=data)
            self.logger.log_action(
                "get_positions",
                account_id=account_id,
                message=f"Retrieved {len(positions.positions)} positions for {account_id}."
            )
            return positions
        except Exception as e:
            self.logger.error(f"Failed to fetch positions for {account_id}: {e}")
            raise

    def get_positions_nocache(
        self,
        account_id: str,
        model: Optional[str] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None
    ) -> PortfolioPositionsResponse:
        """
        Retrieve near-real-time (uncached) portfolio positions for a specific account.
        
        Unlike the paginated 'get_positions' endpoint (/portfolio/{accountId}/positions/{pageId}),
        this endpoint (/portfolio2/{accountId}/positions) bypasses gateway cache and returns
        all positions without pagination.
        
        Args:
            account_id (str): The account ID.
            model (Optional[str]): Code for the model portfolio to compare against.
            sort (Optional[str]): Column to sort the table by.
            direction (Optional[str]): Sort order: 'a' (ascending) or 'd' (descending).
            
        Returns:
            PortfolioPositionsResponse: Validated list of positions.
        """
        self.logger.info(f"Fetching uncached positions for account: {account_id}")
        endpoint = f"/portfolio2/{account_id}/positions"
        
        params = {}
        if model is not None:
            params["model"] = model
        if sort is not None:
            params["sort"] = sort
        if direction is not None:
            params["direction"] = direction
            
        try:
            data = self.client.get(endpoint, params=params)
            # Response is a list of position objects
            positions = PortfolioPositionsResponse(positions=data)
            self.logger.log_action(
                "get_positions_nocache",
                account_id=account_id,
                message=f"Retrieved {len(positions.positions)} uncached positions for {account_id}."
            )
            return positions
        except Exception as e:
            self.logger.error(f"Failed to fetch uncached positions for {account_id}: {e}")
            raise

    def invalidate_positions(self, account_id: str) -> Dict[str, Any]:
        """
        Invalidate the backend cache for portfolio positions.
        
        Args:
            account_id (str): The account ID to invalidate cache for.
            
        Returns:
            Dict[str, Any]: API response metadata.
        """
        self.logger.info(f"Invalidating portfolio positions cache for account: {account_id}")
        endpoint = f"/portfolio/{account_id}/positions/invalidate"
        try:
            data = self.client.post(endpoint)
            self.logger.log_action(
                "invalidate_positions",
                account_id=account_id,
                message=f"Positions cache invalidated for account {account_id}."
            )
            return data
        except Exception as e:
            self.logger.error(f"Failed to invalidate positions cache for {account_id}: {e}")
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

    def get_performance(self, account_ids: List[str], period: str = "12M") -> PAPerformanceResponse:
        """
        Retrieve performance data from Portfolio Analyst.
        
        Args:
            account_ids (List[str]): List of account IDs.
            period (str): Period of data ('1D', '7D', 'MTD', '1M', '3M', '6M', '12M', 'YTD').
            
        Returns:
            PAPerformanceResponse: Validated performance data.
        """
        self.logger.info(f"Fetching PA performance for accounts: {account_ids}, period: {period}")
        endpoint = "/pa/performance"
        
        # Map documented "12M" to the gateway's expected "1Y" to resolve the gateway bug
        gateway_period = "1Y" if period == "12M" else period
        
        payload = {"acctIds": account_ids, "period": gateway_period}
        try:
            data = self.client.post(endpoint, json_data=payload)
            performance = PAPerformanceResponse(**data)
            self.logger.log_action(
                "get_performance",
                message=f"Retrieved performance for {len(account_ids)} accounts.",
                details={"acctIds": account_ids, "period": period}
            )
            return performance
        except Exception as e:
            self.logger.error(f"Failed to fetch PA performance: {e}")
            raise

    def get_performance_all_periods(self, account_ids: List[str]) -> PAPerformanceResponse:
        """
        Retrieve performance data for all periods from Portfolio Analyst.
        
        Args:
            account_ids (List[str]): List of account IDs.
            
        Returns:
            PAPerformanceResponse: Validated performance data for all periods.
        """
        self.logger.info(f"Fetching PA performance all periods for accounts: {account_ids}")
        endpoint = "/pa/allperiods"
        payload = {"acctIds": account_ids}
        try:
            data = self.client.post(endpoint, json_data=payload)
            performance = PAPerformanceResponse(**data)
            self.logger.log_action(
                "get_performance_all_periods",
                message=f"Retrieved performance all periods for {len(account_ids)} accounts.",
                details={"acctIds": account_ids}
            )
            return performance
        except Exception as e:
            self.logger.error(f"Failed to fetch PA performance all periods: {e}")
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

    def get_transactions(self, account_ids: List[str], conids: List[int], currency: str,
                         days: int = 90) -> PATransactionsResponse:
        """
        Retrieve historical transactions from Portfolio Analyst.
        
        Args:
            account_ids (List[str]): List of account IDs (acctIds).
            conids (List[int]): List of contract IDs (conids).
            currency (str): Currency code (e.g. "USD").
            days (int): Number of days to look back. Defaults to 90.
            
        Returns:
            PATransactionsResponse: Validated list of transactions.
        """
        self.logger.info(f"Fetching PA transactions for accounts: {account_ids}")
        endpoint = "/pa/transactions"
        payload = {
            "acctIds": account_ids,
            "conids": conids,
            "currency": currency,
            "days": days
        }
            
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

    def list_subaccounts(self) -> PortfolioSubaccountsResponse:
        """
        Retrieve a list of sub-accounts associated with tiered account structures.
        
        Returns:
            PortfolioSubaccountsResponse: Validated list of sub-accounts.
        """
        self.logger.info("Fetching portfolio subaccounts.")
        endpoint = "/portfolio/subaccounts"
        try:
            data = self.client.get(endpoint)
            subaccounts = PortfolioSubaccountsResponse(subaccounts=data)
            self.logger.log_action(
                "list_subaccounts",
                message=f"Retrieved {len(subaccounts.subaccounts)} sub-accounts."
            )
            return subaccounts
        except Exception as e:
            self.logger.error(f"Failed to fetch portfolio subaccounts: {e}")
            raise

    def get_positions_by_conid(self, conid: int) -> PortfolioPositionsConidResponse:
        """
        Retrieve positions across all accounts for a specific contract ID.
        
        Args:
            conid (int): The contract identifier.
            
        Returns:
            PortfolioPositionsConidResponse: Validated dictionary of positions per account.
        """
        self.logger.info(f"Fetching all account positions for contract: {conid}")
        endpoint = f"/portfolio/positions/{conid}"
        try:
            data = self.client.get(endpoint)
            # Response is a dictionary mapping accountId to list of positions
            positions = PortfolioPositionsConidResponse(data)
            self.logger.log_action(
                "get_positions_by_conid",
                message=f"Retrieved positions across accounts for contract {conid}."
            )
            return positions
        except Exception as e:
            self.logger.error(f"Failed to fetch positions for contract {conid}: {e}")
            raise

    def get_account_meta(self, account_id: str) -> PortfolioAccountMetaResponse:
        """
        Retrieve metadata and attributes for a specific account.
        
        Args:
            account_id (str): The account ID.
            
        Returns:
            PortfolioAccountMetaResponse: Validated metadata/attributes.
        """
        self.logger.info(f"Fetching account metadata for account: {account_id}")
        endpoint = f"/portfolio/{account_id}/meta"
        try:
            data = self.client.get(endpoint)
            meta = PortfolioAccountMetaResponse(**data)
            self.logger.log_action(
                "get_account_meta",
                account_id=account_id,
                message=f"Retrieved metadata for account {account_id}."
            )
            return meta
        except Exception as e:
            self.logger.error(f"Failed to fetch metadata for account {account_id}: {e}")
            raise

    def get_position_by_conid(self, account_id: str, conid: int) -> PortfolioPositionResponse:
        """
        Retrieve position details for a specific financial instrument in an account.
        
        Args:
            account_id (str): The account ID.
            conid (int): The contract identifier.
            
        Returns:
            PortfolioPositionResponse: Validated list of position details.
        """
        self.logger.info(f"Fetching position for contract {conid} in account {account_id}")
        endpoint = f"/portfolio/{account_id}/position/{conid}"
        try:
            data = self.client.get(endpoint)
            positions = PortfolioPositionResponse(positions=data)
            self.logger.log_action(
                "get_position_by_conid",
                account_id=account_id,
                message=f"Retrieved position for contract {conid} in account {account_id}."
            )
            return positions
        except Exception as e:
            self.logger.error(f"Failed to fetch position for contract {conid} in account {account_id}: {e}")
            raise

    def get_pa_allocation(self, account_ids: List[str], type: str, 
                          currency: Optional[str] = None, date: Optional[str] = None, 
                          model: Optional[str] = None) -> PAAllocationResponse:
        """
        Retrieve consolidated Portfolio Analyst allocation.
        
        Args:
            account_ids (List[str]): List of account IDs.
            type (str): The allocation category ('ALL', 'ASSET_CLASS', 'COUNTRY', 'FINANCIAL_INSTRUMENT', 'REGION', 'SECTOR').
            currency (Optional[str]): Optional currency code to filter or aggregate by.
            date (Optional[str]): Optional reporting date.
            model (Optional[str]): Optional model identifier.
            
        Returns:
            PAAllocationResponse: Validated consolidated allocation.
        """
        self.logger.info(f"Fetching consolidated PA allocation for accounts: {account_ids}, type: {type}")
        endpoint = "/pa/allocation"
        payload = {
            "acctIds": account_ids,
            "type": type
        }
        if currency is not None:
            payload["currency"] = currency
        if date is not None:
            payload["date"] = date
        if model is not None:
            payload["model"] = model

        try:
            data = self.client.post(endpoint, json_data=payload)
            allocations = PAAllocationResponse(**data)
            self.logger.log_action(
                "get_pa_allocation",
                message=f"Retrieved consolidated PA allocation for {len(account_ids)} accounts.",
                details=payload
            )
            return allocations
        except Exception as e:
            self.logger.error(f"Failed to fetch consolidated PA allocation: {e}")
            raise
