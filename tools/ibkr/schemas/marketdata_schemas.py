"""
Pydantic schemas for the IBKR Market Data tool.
This module defines the validation models for historical bar data
as specified in the Interactive Brokers Client Portal API documentation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union

class HistoricalBar(BaseModel):
    """
    Validation schema for a single historical bar (OHLCV).
    """
    o: Optional[float] = Field(None, description="Open price")
    c: Optional[float] = Field(None, description="Close price")
    h: Optional[float] = Field(None, description="High price")
    l: Optional[float] = Field(None, description="Low price")
    v: Optional[float] = Field(None, description="Volume")
    t: Optional[int] = Field(None, description="Timestamp (Unix epoch in milliseconds)")
    model_config = {"extra": "allow"}

class HistoricalDataResponse(BaseModel):
    """
    Validation schema for response from /iserver/marketdata/history.
    """
    serverId: Optional[str] = Field(None, description="Server ID")
    symbol: Optional[str] = Field(None, description="Ticker symbol")
    text: Optional[str] = Field(None, description="Instrument description")
    priceFactor: Optional[int] = Field(None, description="Price factor")
    startTime: Optional[str] = Field(None, description="Start time of data period")
    timePeriod: Optional[str] = Field(None, description="Requested time period")
    barLength: Optional[int] = Field(None, description="Length of bar in seconds")
    data: List[HistoricalBar] = Field(default=[], description="List of historical OHLCV bars")
    points: Optional[int] = Field(None, description="Number of data points")
    travelTime: Optional[int] = Field(None, description="Travel time or latency")
    model_config = {"extra": "allow"}
