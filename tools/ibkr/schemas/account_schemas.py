"""
Pydantic schemas for the IBKR Accounts tool.
This module defines the validation models for account-related data
as specified in the Interactive Brokers Client Portal API documentation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class BrokerageAccountsResponse(BaseModel):
    """
    Validation schema for the response from /iserver/accounts.
    Returns all accessible accounts, aliases, and session information.
    """
    accounts: List[str] = Field(..., description="List of accessible account IDs")
    aliases: Dict[str, str] = Field(default={}, description="Mapping of account IDs to aliases")
    selectedAccount: str = Field(..., description="The currently selected account ID for the session")
    isContextRefreshed: Optional[bool] = Field(None, description="Whether the context was refreshed")

class PnLPartition(BaseModel):
    """
    Validation schema for an individual PnL partition or row.
    """
    rowType: int = Field(..., description="1 for individual, other values for partitions")
    pnl: Optional[float] = Field(None, description="Profit and Loss value")
    dpl: Optional[float] = Field(None, description="Daily Profit and Loss")
    upl: Optional[float] = Field(None, description="Unrealized Profit and Loss")
    rpl: Optional[float] = Field(None, description="Realized Profit and Loss")

class AccountPnLResponse(BaseModel):
    """
    Validation schema for the response from /iserver/account/pnl/partitioned.
    Returns Profit and Loss for the selected account and models.
    """
    # Keys in the response are typically account IDs mapping to their PnL data
    acctId: Dict[str, PnLPartition] = Field(..., description="PnL data partitioned by account or model")

class SignatureOwnerInfo(BaseModel):
    """
    Validation schema for account signatures and owners from /acesws/{accountID}/signatures-and-owners.
    """
    accountID: str = Field(..., description="The account identifier")
    entityType: str = Field(..., description="The type of entity (e.g., INDIVIDUAL, JOINT)")
    applicants: List[Dict[str, Any]] = Field(..., description="List of account owners and applicants")
