"""
Pydantic schemas for the IBKR Accounts tool.
This module defines the validation models for account-related data
as specified in the Interactive Brokers Client Portal API documentation.
"""
from pydantic import BaseModel, Field, RootModel
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
    upnl: Dict[str, PnLPartition] = Field(..., description="Unrealized PnL data partitioned by account or model")

class EntityInfo(BaseModel):
    firstName: str = Field(..., description="First name of the entity")
    lastName: str = Field(..., description="Last name of the entity")
    entityType: str = Field(..., description="Type of the entity (e.g., INDIVIDUAL)")
    entityName: str = Field(..., description="Full name of the entity")
    dateOfBirth: str = Field(..., description="Date of birth (YYYY-MM-DD)")

class UserInfo(BaseModel):
    roleId: str = Field(..., description="Role ID of the user (e.g., OWNER)")
    hasRightCodeInd: bool = Field(..., description="Indicates if the user has right code")
    userName: str = Field(..., description="User name")
    entity: EntityInfo = Field(..., description="Entity information for the user")

class ApplicantSignatures(BaseModel):
    signatures: List[str] = Field(..., description="List of signatures for the applicant")

class SignatureOwnerInfo(BaseModel):
    """
    Validation schema for the response from /acesws/{accountID}/signatures-and-owners.
    """
    accountId: str = Field(..., description="The account identifier")
    users: List[UserInfo] = Field(..., description="List of user information for the account")
    applicant: ApplicantSignatures = Field(..., description="Applicant information including signatures")

class DynamicAccountInfo(BaseModel):
    """
    Validation schema for a single dynamic account from /iserver/account/search/{searchPattern}.
    """
    accountId: str = Field(..., description="The ID of the dynamic account")
    accountName: str = Field(..., description="The name of the dynamic account")

class DynamicAccountsResponse(BaseModel):
    """
    Validation schema for the response from /iserver/account/search/{searchPattern}.
    Returns a list of dynamic accounts matching the search pattern.
    """
    accounts: List[DynamicAccountInfo] = Field(..., description="List of dynamic accounts")

class AmountCurrency(BaseModel):
    """
    Validation schema for an amount and currency pair.
    """
    amount: float = Field(..., description="The monetary amount")
    currency: str = Field(..., description="The currency (e.g., USD)")

class CashBalance(BaseModel):
    """
    Validation schema for individual cash balance entries.
    """
    currency: str = Field(..., description="Currency of the cash balance")
    balance: float = Field(..., description="Cash balance amount")
    settledCash: float = Field(..., description="Settled cash amount")

class AccountSummaryResponse(BaseModel):
    """
    Validation schema for the response from /iserver/account/{accountId}/summary.
    Returns a comprehensive summary of account values, balances, and margins.
    """
    accountId: Optional[str] = Field(None, description="The account identifier")
    accountType: Optional[str] = Field(None, description="Type of account")
    status: Optional[str] = Field(None, description="Account status")
    balance: Optional[float] = Field(None, description="Current balance")
    SMA: Optional[float] = Field(None, description="Special Memorandum Account (SMA)")
    buyingPower: Optional[float] = Field(None, description="Buying power")
    availableFunds: Optional[float] = Field(None, description="Available funds")
    excessLiquidity: Optional[float] = Field(None, description="Excess liquidity")
    netLiquidationValue: Optional[float] = Field(None, description="Net liquidation value")
    equityWithLoanValue: Optional[float] = Field(None, description="Equity with loan value")
    regTLoan: Optional[float] = Field(None, description="Reg T loan")
    securitiesGVP: Optional[float] = Field(None, description="Securities gross value of positions")
    totalCashValue: Optional[float] = Field(None, description="Total cash value")
    accruedInterest: Optional[float] = Field(None, description="Accrued interest")
    regTMargin: Optional[float] = Field(None, description="Reg T margin")
    initialMargin: Optional[float] = Field(None, description="Initial margin")
    maintenanceMargin: Optional[float] = Field(None, description="Maintenance margin")
    cashBalances: Optional[List[CashBalance]] = Field(None, description="List of cash balances by currency")

class TotalFundsSummary(BaseModel):
    """
    Validation schema for the 'total' funds summary object.
    """
    current_available: str = Field(..., description="Current available funds")
    current_excess: str = Field(..., description="Current excess liquidity")
    Prdctd_Pst_xpry_Excss: str = Field(..., alias="Prdctd Pst-xpry Excss", description="Predicted post-expiry excess")
    Lk_Ahd_Avlbl_Fnds: str = Field(..., alias="Lk Ahd Avlbl Fnds", description="Look ahead available funds")
    Lk_Ahd_Excss_Lqdty: str = Field(..., alias="Lk Ahd Excss Lqdty", description="Look ahead excess liquidity")
    overnight_available: str = Field(..., description="Overnight available funds")
    overnight_excess: str = Field(..., description="Overnight excess liquidity")
    buying_power: str = Field(..., description="Buying power")
    leverage: str = Field(..., description="Leverage")
    Lk_Ahd_Nxt_Chng: str = Field(..., alias="Lk Ahd Nxt Chng", description="Look ahead next change")

class CFDSummary(BaseModel):
    """
    Validation schema for the 'cfd' summary object.
    """
    leverage: str = Field(..., description="CFD leverage")

class AvailableFundsResponse(BaseModel):
    """
    Validation schema for the response from /iserver/account/{accountId}/summary/available_funds.
    Returns a comprehensive summary of available funds, including total and CFD specific details.
    """
    total: TotalFundsSummary = Field(..., description="Total funds summary")
    cfd: CFDSummary = Field(..., description="CFD specific summary")

class TotalBalancesSummary(BaseModel):
    """
    Validation schema for the "total" balances summary object.
    """
    net_liquidation: str = Field(..., description="Net liquidation value")
    Nt_Lqdtn_Uncrtnty: str = Field(..., alias="Nt Lqdtn Uncrtnty", description="Net liquidation uncertainty")
    equity_with_loan: str = Field(..., description="Equity with loan value")
    sec_gross_pos_val: str = Field(..., description="Securities gross value of positions")
    cash: str = Field(..., description="Cash balance")
    MTD_Interest: str = Field(..., alias="MTD Interest", description="Month-to-date interest")

class CFDBalancesSummary(BaseModel):
    """
    Validation schema for the "cfd" balances summary object.
    """
    # Currently empty, can be extended if CFD balances data becomes available
    pass

class AccountBalancesResponse(BaseModel):
    """
    Validation schema for the response from /iserver/account/{accountId}/summary/balances.
    Returns a comprehensive summary of account balances, including total and CFD specific details.
    """
    total: TotalBalancesSummary = Field(..., description="Total balances summary")
    cfd: CFDBalancesSummary = Field(..., description="CFD specific balances summary")

class TotalMarginSummary(BaseModel):
    """
    Validation schema for the "total" margin summary object.
    """
    current_initial: str = Field(..., description="Current initial margin")
    Prdctd_Pst_xpry_Mrgn_Opn: str = Field(..., alias="Prdctd Pst-xpry Mrgn @ Opn", description="Predicted post-expiry margin at open")
    current_maint: str = Field(..., description="Current maintenance margin")
    projected_liquidity_inital_margin: str = Field(..., description="Projected liquidity initial margin")
    Prjctd_Lk_Ahd_Mntnnc_Mrgn: str = Field(..., alias="Prjctd Lk Ahd Mntnnc Mrgn", description="Projected look ahead maintenance margin")
    projected_overnight_initial_margin: str = Field(..., description="Projected overnight initial margin")
    Prjctd_Ovrnght_Mntnnc_Mrgn: str = Field(..., alias="Prjctd Ovrnght Mntnnc Mrgn", description="Projected overnight maintenance margin")

class CFDMarginSummary(BaseModel):
    """
    Validation schema for the "cfd" margin summary object.
    """
    # Currently empty, can be extended if CFD margin data becomes available
    pass

class AccountMarginResponse(BaseModel):
    """
    Validation schema for the response from /iserver/account/{accountId}/summary/margins.
    Returns a comprehensive summary of account margin usage, including total and CFD specific details.
    """
    total: TotalMarginSummary = Field(..., description="Total margin summary")
    cfd: CFDMarginSummary = Field(..., description="CFD specific margin summary")

class CurrencyMarketValueDetails(BaseModel):
    """
    Validation schema for currency-specific market value details.
    """
    total_cash: str = Field(..., description="Total cash value in this currency")
    settled_cash: str = Field(..., description="Settled cash in this currency")
    MTD_Interest: str = Field(..., alias="MTD Interest", description="Month-to-date interest in this currency")
    stock: str = Field(..., description="Stock value in this currency")
    options: str = Field(..., description="Options value in this currency")
    futures: str = Field(..., description="Futures value in this currency")
    future_options: str = Field(..., description="Future options value in this currency")
    funds: str = Field(..., description="Funds value in this currency")
    dividends_receivable: str = Field(..., description="Dividends receivable in this currency")
    mutual_funds: str = Field(..., description="Mutual funds value in this currency")
    money_market: str = Field(..., description="Money market value in this currency")
    bonds: str = Field(..., description="Bonds value in this currency")
    Govt_Bonds: str = Field(..., alias="Govt Bonds", description="Government bonds value in this currency")
    t_bills: str = Field(..., description="Treasury bills value in this currency")
    warrants: str = Field(..., description="Warrants value in this currency")
    issuer_option: str = Field(..., description="Issuer options value in this currency")
    commodity: str = Field(..., description="Commodity value in this currency")
    Notional_CFD: str = Field(..., alias="Notional CFD", description="Notional CFD value in this currency")
    cfd: str = Field(..., description="CFD value in this currency")
    Cryptocurrency: Optional[str] = Field(None, description="Cryptocurrency value in this currency")
    net_liquidation: str = Field(..., description="Net liquidation value in this currency")
    unrealized_pnl: str = Field(..., description="Unrealized PnL in this currency")
    realized_pnl: str = Field(..., description="Realized PnL in this currency")
    Exchange_Rate: str = Field(..., alias="Exchange Rate", description="Exchange rate to base currency")

class AccountMarketValueResponse(RootModel[Dict[str, CurrencyMarketValueDetails]]):
    """
    Validation schema for the response from /iserver/account/{accountId}/summary/market_value.
    Returns a dictionary where keys are currency codes and values are detailed market value summaries.
    """
    root: Dict[str, CurrencyMarketValueDetails] = Field(..., description="Market value details by currency")

class SetDynamicAccountRequest(BaseModel):
    """
    Request body schema for POST /iserver/dynaccount.
    Used to set the active dynamic account.
    """
    accountId: str = Field(..., description="The account ID to set as active dynamic account")

class SetDynamicAccountResponse(BaseModel):
    """
    Response schema for POST /iserver/dynaccount.
    Confirms the active dynamic account has been set.
    """
    dynamicAccount: str = Field(..., description="The newly set active dynamic account ID")
    message: Optional[str] = Field(None, description="A confirmation message")
