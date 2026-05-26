"""
IBKR Market Data Tool.
This tool provides functionality to retrieve historical OHLC bar data
from the Interactive Brokers Client Portal API.
"""
from .core import MarketDataManager

__all__ = ["MarketDataManager"]
