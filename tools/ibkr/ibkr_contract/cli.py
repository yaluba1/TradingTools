"""
CLI interface for the IBKR Contract tool.
This module provides the command-line arguments and handlers for interacting
with the ContractManager.
"""
import argparse
import sys
import json
from .core import ContractManager

def main():
    """
    Main entry point for the IBKR Contract CLI.
    
    This tool provides subcommands for querying security contracts:
    
    * **search**: Search for contracts by ticker symbol. Requires --symbol.
    * **details**: Get detailed contract info and rules. Requires --conid.
    * **strikes**: Get available option strikes for an underlying. Requires --conid, --type, --month.
    * **schedule**: Get trading schedule for an instrument. Requires --conid.
    """
    parser = argparse.ArgumentParser(description="IBKR Contract Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search for contracts by symbol")
    search_parser.add_argument("--symbol", required=True, help="Ticker symbol (e.g., AAPL)")

    # Details subcommand
    details_parser = subparsers.add_parser("details", help="Get detailed contract info and rules")
    details_parser.add_argument("--conid", required=True, help="Contract ID")
    details_parser.add_argument("--type", default="STK", help="Security type (default: STK)")

    # Strikes subcommand
    strikes_parser = subparsers.add_parser("strikes", help="Get available option strikes")
    strikes_parser.add_argument("--conid", required=True, help="Underlying contract ID")
    strikes_parser.add_argument("--type", required=True, help="Security type (e.g., OPT)")
    strikes_parser.add_argument("--month", required=True, help="Contract month (e.g., OCT24)")
    strikes_parser.add_argument("--exchange", default="SMART", help="Exchange (default: SMART)")

    # Schedule subcommand
    schedule_parser = subparsers.add_parser("schedule", help="Get trading schedule for an instrument")
    schedule_parser.add_argument("--conid", required=True, help="Contract ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    manager = ContractManager()

    try:
        if args.command == "search":
            result = manager.search_contracts(args.symbol)
            # Pydantic v2 model_dump() with RootModel needs ["root"] to get the list.
            print(json.dumps(result.model_dump()["root"], indent=2))
            
        elif args.command == "details":
            result = manager.get_contract_details(args.conid, args.type)
            print(json.dumps(result.model_dump()["root"], indent=2))
            
        elif args.command == "strikes":
            result = manager.get_strikes(args.conid, args.type, args.month, args.exchange)
            print(json.dumps(result.model_dump(), indent=2))
            
        elif args.command == "schedule":
            result = manager.get_trading_schedule(args.conid)
            print(json.dumps(result.model_dump()["root"], indent=2))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
