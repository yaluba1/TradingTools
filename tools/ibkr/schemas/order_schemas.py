"""
Pydantic schemas for the IBKR Orders tool.
This module defines the validation models for order-related data, including
requests for placement/modification and responses for status monitoring.
"""
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class OrderRequest(BaseModel):
    """
    Schema for a single order placement or modification request.
    This corresponds to the structure expected by /iserver/account/{accountId}/orders.
    """
    conid: int = Field(..., description="Unique contract identifier")
    secType: str = Field("STK", description="Security type (e.g., STK, OPT, FUT)")
    orderType: str = Field(..., description="Order type (e.g., LMT, MKT, STP)")
    side: str = Field(..., description="Order side (BUY or SELL)")
    quantity: float = Field(..., description="Order quantity")
    price: Optional[float] = Field(None, description="Limit price (for LMT orders)")
    auxPrice: Optional[float] = Field(None, description="Auxiliary price (e.g., for STP orders)")
    tif: str = Field("DAY", description="Time in force (e.g., DAY, GTC)")
    listingExchange: Optional[str] = Field(None, description="Destination exchange")
    outsideRth: bool = Field(False, description="Whether to allow trading outside regular trading hours")
    referrer: Optional[str] = Field("OpenClaw", description="Order source identifier")
    useAdaptive: bool = Field(False, description="Whether to use IBKR adaptive algo")
    cId: Optional[str] = Field(None, description="Customer-defined order ID for tracking")

class OrderPlacementResponse(BaseModel):
    """
    Schema for a response from the order placement endpoint.
    IBKR may return either a direct success result or a confirmation requirement.
    """
    order_id: Optional[str] = Field(None, description="The server-assigned order ID")
    order_status: Optional[str] = Field(None, description="Current status of the order")
    local_order_id: Optional[str] = Field(None, description="Customer ID used")
    id: Optional[str] = Field(None, description="Confirmation message ID (if reply required)")
    message: Optional[List[str]] = Field(None, description="Messages/Questions from IBKR")

class OrderPlacementResults(RootModel):
    """
    The /orders endpoint returns a list of results (one per order in the request).
    """
    root: List[OrderPlacementResponse]

class OrderReplyRequest(BaseModel):
    """
    Schema for replying to an IBKR confirmation/question.
    """
    confirmed: bool = Field(True, description="Whether to confirm the warning/question")

class LiveOrder(BaseModel):
    """
    Schema for an order in the live monitoring list (/iserver/account/orders).
    """
    orderId: Optional[Union[int, str]] = Field(None, description="Server order ID")
    conid: int = Field(..., description="Contract ID")
    ticker: Optional[str] = Field(None, description="Symbol/Ticker")
    side: str = Field(..., description="BUY or SELL")
    orderType: str = Field(..., description="LMT, MKT, etc.")
    totalSize: float = Field(..., description="Original quantity")
    cumFill: float = Field(0.0, description="Cumulative filled quantity")
    avgPrice: float = Field(0.0, description="Average fill price")
    status: str = Field(..., description="PendingSubmit, Filled, Cancelled, etc.")
    lmtPrice: Optional[float] = Field(None, description="Limit price")
    auxPrice: Optional[float] = Field(None, description="Aux/Stop price")
    timeInForce: str = Field(..., description="DAY, GTC, etc.")
    lastExecutionTime_p: Optional[str] = Field(None, description="Last execution time (formatted)")
    account: str = Field(..., description="Account ID")

class OrderHistoryResponse(RootModel):
    """
    Schema for the live orders list response.
    """
    root: Dict[str, List[LiveOrder]] # Keyed by account ID usually, or just a list depending on endpoint

class SyncOrderResult(BaseModel):
    """
    Result of a synchronization operation between IBKR and the local database.
    """
    customer_order_id: str
    status_changed: bool
    old_status: str
    new_status: str
    filled_increment: float
    event_logged: bool

class QuestionInfo(BaseModel):
    """
    Schema for a system question or prompt from IBKR (/iserver/questions).
    """
    id: str = Field(..., description="Unique identifier for the question")
    text: List[str] = Field(..., description="The content/question lines from IBKR")
