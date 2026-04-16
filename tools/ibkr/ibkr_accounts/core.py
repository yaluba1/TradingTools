"""
Core logic for the IBKR Accounts tool.
This module provides the AccountsManager class to interact with IBKR account endpoints,
supporting brokerage account listing, PnL tracking, and ownership information retrieval.
"""
from typing import List, Dict, Any, Optional
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..schemas.account_schemas import (
    BrokerageAccountsResponse,
    AccountPnLResponse,
    SignatureOwnerInfo,
    DynamicAccountsResponse,
    AccountSummaryResponse,
    AvailableFundsResponse,
    AccountBalancesResponse,
    AccountMarginResponse,
    AccountMarketValueResponse,
    SetDynamicAccountRequest,
    SetDynamicAccountResponse
)

class AccountsManager:
    """
    Manager for IBKR account-related operations.
    
    This class wraps the /iserver and /acesws endpoints related to account management
    for individual users, ensuring all actions are logged and validated.
    """
    def __init__(self):
        """
        Initialize the AccountsManager.
        
        Sets up the API client with pacing support and the logger for dual
        file/database recording.
        """
        self.tool_name = "accounts"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def list_accounts(self) -> BrokerageAccountsResponse:
        """
        Retrieve all brokerage accounts associated with the current session.
        
        According to the IBKR API, this endpoint must be called before modifying 
        or querying orders to initialize the session context correctly.

        Returns:
            BrokerageAccountsResponse: A validated object containing accounts, 
                                     aliases, and the currently selected account.
        
        Raises:
            Exception: If the API request fails or the response does not match the schema.
        """
        self.logger.info("Fetching brokerage accounts.")
        endpoint = "/iserver/accounts"
        try:
            data = self.client.get(endpoint)
            # The API returns an object with 'accounts', 'aliases', and 'selectedAccount'.
            accounts_data = BrokerageAccountsResponse(**data)
            self.logger.log_action(
                "list_accounts", 
                message=f"Retrieved {len(accounts_data.accounts)} accounts.",
                details={"accounts": accounts_data.accounts, "selected": accounts_data.selectedAccount}
            )
            return accounts_data
        except Exception as e:
            self.logger.error(f"Failed to fetch accounts list: {e}")
            raise

    def get_pnl(self) -> AccountPnLResponse:
        """
        Retrieve Profit and Loss (PnL) data for the accounts in the current session.
        
        PnL data includes daily, realized, and unrealized values, potentially 
        partitioned by account or model for individual structures.

        Returns:
            AccountPnLResponse: A validated object containing PnL data mapping.
        
        Raises:
            Exception: If the API request fails.
        """
        self.logger.info("Fetching PnL data for the session.")
        endpoint = "/iserver/account/pnl/partitioned"
        try:
            data = self.client.get(endpoint)
            # The response is a dictionary where keys are account identifiers.
            pnl_data = AccountPnLResponse.model_validate(data)
            self.logger.log_action("get_pnl", message="Retrieved PnL data successfully.")
            return pnl_data
        except Exception as e:
            self.logger.error(f"Failed to fetch PnL data: {e}")
            raise

    def get_signatures_and_owners(self, account_id: str) -> SignatureOwnerInfo:
        """
        Retrieve signature and ownership information for a specific account.
        
        This includes detailed user roles, entity information (e.g., individual details),
        and applicant signatures as provided by the IBKR Client Portal API.

        Args:
            account_id (str): The account ID to query (e.g., \'U1234567\').

        Returns:
            SignatureOwnerInfo: A validated object containing comprehensive ownership details,
                                 including a list of users and applicant signatures.
        
        Raises:
            Exception: If the API request fails or the account ID is invalid.
        """
        self.logger.info(f"Fetching signatures and owners for account: {account_id}")
        endpoint = f"/acesws/{account_id}/signatures-and-owners"
        try:
            data = self.client.get(endpoint)
            owner_info = SignatureOwnerInfo.model_validate(data)
            self.logger.log_action(
                "get_signatures", 
                account_id=account_id,
                message=f"Retrieved ownership info for account {account_id}.",
                details={
                    "entityType": owner_info.users[0].entity.entityType if owner_info.users else "N/A",
                    "applicantCount": len(owner_info.applicant.signatures) if owner_info.applicant and owner_info.applicant.signatures else 0
                }
            )
            return owner_info
        except Exception as e:
            self.logger.error(f"Failed to fetch ownership information for {account_id}: {e}")
            raise

    def search_dynamic_accounts(self, search_pattern: str) -> DynamicAccountsResponse:
        """
        Search for dynamic accounts by a specified pattern.

        Args:
            search_pattern (str): The pattern to use for searching accounts.

        Returns:
            DynamicAccountsResponse: A validated object containing a list of dynamic accounts.

        Raises:
            Exception: If the API request fails.
        """
        self.logger.info(f"Searching dynamic accounts with pattern: {search_pattern}")
        endpoint = f"/iserver/account/search/{search_pattern}"
        try:
            data = self.client.get(endpoint)
            accounts_data = DynamicAccountsResponse.model_validate({"accounts": data})
            self.logger.log_action(
                "search_dynamic_accounts",
                message=f"Found {len(accounts_data.accounts)} dynamic accounts for pattern {search_pattern}.",
                details={"search_pattern": search_pattern, "found_accounts": [acc.accountId for acc in accounts_data.accounts]}
            )
            return accounts_data
        except Exception as e:
            self.logger.error(f"Failed to search dynamic accounts: {e}")
            raise

    def get_account_summary(self, account_id: str) -> AccountSummaryResponse:
        """
        Retrieve a summary of account values for a specific account.

        Args:
            account_id (str): The ID of the account for which to retrieve the summary.

        Returns:
            AccountSummaryResponse: A validated object containing the summary of account values.

        Raises:
            Exception: If the API request fails or the response does not match the schema.
        """
        self.logger.info(f"Fetching account summary for account: {account_id}")
        endpoint = f"/iserver/account/{account_id}/summary"
        try:
            data = self.client.get(endpoint)
            account_summary = AccountSummaryResponse.model_validate(data)
            self.logger.log_action(
                "get_account_summary",
                account_id=account_id,
                message=f"Retrieved account summary for {account_id}.",
                details={
                    "netLiquidationValue": account_summary.netLiquidationValue if account_summary.netLiquidationValue is not None else "N/A",
                    "availableFunds": account_summary.availableFunds if account_summary.availableFunds is not None else "N/A",
                    "buyingPower": account_summary.buyingPower if account_summary.buyingPower is not None else "N/A"
                }
            )
            return account_summary
        except Exception as e:
            self.logger.error(f"Failed to fetch account summary for {account_id}: {e}")
            raise

    def get_available_funds(self, account_id: str) -> AvailableFundsResponse:
        """
        Retrieve a summary of available funds for a specific account.

        Args:
            account_id (str): The ID of the account for which to retrieve available funds.

        Returns:
            AvailableFundsResponse: A validated object containing the summary of available funds.

        Raises:
            Exception: If the API request fails or the response does not match the schema.
        """
        self.logger.info(f"Fetching available funds for account: {account_id}")
        endpoint = f"/iserver/account/{account_id}/summary/available_funds"
        try:
            data = self.client.get(endpoint)
            available_funds = AvailableFundsResponse.model_validate(data)
            self.logger.log_action(
                "get_available_funds",
                account_id=account_id,
                message=f"Retrieved available funds for {account_id}.",
                details={
                    "current_available": available_funds.total.current_available if available_funds.total else "N/A",
                    "buying_power": available_funds.total.buying_power if available_funds.total else "N/A",
                    "cfd_leverage": available_funds.cfd.leverage if available_funds.cfd else "N/A"
                }
            )
            return available_funds
        except Exception as e:
            self.logger.error(f"Failed to fetch available funds for {account_id}: {e}")
            raise

    def get_account_balances(self, account_id: str) -> AccountBalancesResponse:
        """
        Retrieve a summary of account balances for a specific account.

        Args:
            account_id (str): The ID of the account for which to retrieve balances.

        Returns:
            AccountBalancesResponse: A validated object containing the summary of account balances.

        Raises:
            Exception: If the API request fails or the response does not match the schema.
        """
        self.logger.info(f"Fetching account balances for account: {account_id}")
        endpoint = f"/iserver/account/{account_id}/summary/balances"
        try:
            data = self.client.get(endpoint)
            account_balances = AccountBalancesResponse.model_validate(data)
            self.logger.log_action(
                "get_account_balances",
                account_id=account_id,
                message=f"Retrieved account balances for {account_id}.",
                details={
                    "net_liquidation": account_balances.total.net_liquidation if account_balances.total else "N/A",
                    "cash": account_balances.total.cash if account_balances.total else "N/A",
                    "mtd_interest": account_balances.total.MTD_Interest if account_balances.total else "N/A"
                }
            )
            return account_balances
        except Exception as e:
            self.logger.error(f"Failed to fetch account balances for {account_id}: {e}")
            raise

    def get_margin_summary(self, account_id: str) -> AccountMarginResponse:
        """
        Retrieve a summary of account margin usage for a specific account.

        Args:
            account_id (str): The ID of the account for which to retrieve margin usage.

        Returns:
            AccountMarginResponse: A validated object containing the summary of account margin usage.

        Raises:
            Exception: If the API request fails or the response does not match the schema.
        """
        self.logger.info(f"Fetching account margin summary for account: {account_id}")
        endpoint = f"/iserver/account/{account_id}/summary/margins"
        try:
            data = self.client.get(endpoint)
            margin_summary = AccountMarginResponse.model_validate(data)
            self.logger.log_action(
                "get_margin_summary",
                account_id=account_id,
                message=f"Retrieved account margin summary for {account_id}.",
                details={
                    "current_initial": margin_summary.total.current_initial if margin_summary.total else "N/A",
                    "current_maint": margin_summary.total.current_maint if margin_summary.total else "N/A"
                }
            )
            return margin_summary
        except Exception as e:
            self.logger.error(f"Failed to fetch account margin summary for {account_id}: {e}")
            raise

    def get_market_value_summary(self, account_id: str) -> AccountMarketValueResponse:
        """
        Retrieve a summary of account market value for a specific account.

        Args:
            account_id (str): The ID of the account for which to retrieve market value.

        Returns:
            AccountMarketValueResponse: A validated object containing the summary of account market value by currency.

        Raises:
            Exception: If the API request fails or the response does not match the schema.
        """
        self.logger.info(f"Fetching account market value summary for account: {account_id}")
        endpoint = f"/iserver/account/{account_id}/summary/market_value"
        try:
            data = self.client.get(endpoint)
            market_value_summary = AccountMarketValueResponse.model_validate(data)
            # Extract summary for logging - get the first currency's net_liquidation
            summary_details = {}
            if market_value_summary.root:
                first_currency = next(iter(market_value_summary.root.keys()), "N/A")
                if first_currency in market_value_summary.root:
                    summary_details = {
                        "primary_currency": first_currency,
                        "net_liquidation": market_value_summary.root[first_currency].net_liquidation,
                        "currencies_count": len(market_value_summary.root)
                    }
            self.logger.log_action(
                "get_market_value_summary",
                account_id=account_id,
                message=f"Retrieved account market value summary for {account_id} ({len(market_value_summary.root)} currencies).",
                details=summary_details
            )
            return market_value_summary
        except Exception as e:
            self.logger.error(f"Failed to fetch account market value summary for {account_id}: {e}")
            raise

    def set_dynamic_account(self, account_id: str) -> SetDynamicAccountResponse:
        """
        Set a specific account as the active dynamic account for the session.

        Args:
            account_id (str): The ID of the account to set as the active dynamic account.

        Returns:
            SetDynamicAccountResponse: A validated object confirming the active dynamic account has been set.

        Raises:
            Exception: If the API request fails or the response does not match the schema.
        """
        self.logger.info(f"Setting dynamic account to: {account_id}")
        endpoint = "/iserver/dynaccount"
        request_body = SetDynamicAccountRequest(accountId=account_id).model_dump_json()
        try:
            data = self.client.post(endpoint, data=request_body)
            dynamic_account_response = SetDynamicAccountResponse.model_validate(data)
            self.logger.log_action(
                "set_dynamic_account",
                account_id=account_id,
                message=f"Dynamic account set to {dynamic_account_response.dynamicAccount}.",
                details={"dynamicAccount": dynamic_account_response.dynamicAccount}
            )
            return dynamic_account_response
        except Exception as e:
            self.logger.error(f"Failed to set dynamic account to {account_id}: {e}")
            raise
