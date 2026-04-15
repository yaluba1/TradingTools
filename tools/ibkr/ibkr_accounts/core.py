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
    SignatureOwnerInfo
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
            pnl_data = AccountPnLResponse(acctId=data)
            self.logger.log_action("get_pnl", message="Retrieved PnL data successfully.")
            return pnl_data
        except Exception as e:
            self.logger.error(f"Failed to fetch PnL data: {e}")
            raise

    def get_signatures_and_owners(self, account_id: str) -> SignatureOwnerInfo:
        """
        Retrieve signature and ownership information for a specific account.
        
        This includes entity types (e.g., INDIVIDUAL) and applicant details.

        Args:
            account_id (str): The account ID to query (e.g., 'U1234567').

        Returns:
            SignatureOwnerInfo: A validated object containing ownership details.
        
        Raises:
            Exception: If the API request fails or the account ID is invalid.
        """
        self.logger.info(f"Fetching signatures and owners for account: {account_id}")
        endpoint = f"/acesws/{account_id}/signatures-and-owners"
        try:
            data = self.client.get(endpoint)
            owner_info = SignatureOwnerInfo(**data)
            self.logger.log_action(
                "get_signatures", 
                account_id=account_id,
                message=f"Retrieved ownership info for account {account_id}.",
                details={"entityType": owner_info.entityType, "applicantCount": len(owner_info.applicants)}
            )
            return owner_info
        except Exception as e:
            self.logger.error(f"Failed to fetch ownership information for {account_id}: {e}")
            raise
