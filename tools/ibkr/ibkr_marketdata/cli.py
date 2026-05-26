"""
CLI interface for the IBKR Market Data tool.
This module provides the command-line arguments and handlers for interacting
with the MarketDataManager.
"""
import argparse
import sys
import json
from .core import MarketDataManager

def main():
    """
    Main entry point for the IBKR Market Data CLI.
    
    This tool provides subcommands for querying market data:
    
    * **history**: Retrieve historical OHLC bar data for a contract.
    """
    parser = argparse.ArgumentParser(description="IBKR Market Data Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # History subcommand
    history_parser = subparsers.add_parser("history", help="Get historical OHLC bar data")
    history_parser.add_argument("--conid", required=True, type=int, help="Contract ID of the instrument")
    history_parser.add_argument("--period", required=True, help="Total duration of data to retrieve (e.g., 1d, 1w, 1m, 1y)")
    history_parser.add_argument("--bar", required=True, help="Granularity of each bar (e.g., 1min, 5min, 1h, 1d)")
    history_parser.add_argument("--outside-rth", action="store_true", help="Include data outside regular trading hours (RTH)")
    history_parser.add_argument("--bar-type", help="Price type: last, midprice, bid, ask, inventory")
    history_parser.add_argument("--start-time", help="Start date/time (YYYYMMDD-hh:mm:ss)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    manager = MarketDataManager()

    try:
        if args.command == "history":
            result = manager.get_historical_data(
                conid=args.conid,
                period=args.period,
                bar=args.bar,
                outsideRth=args.outside_rth if args.outside_rth else None,
                barType=args.bar_type,
                startTime=args.start_time
            )
            print(json.dumps(result.model_dump(), indent=2))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
