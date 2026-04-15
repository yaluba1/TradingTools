"""
CLI interface for the IBKR Portfolio tool.
This module provides the command-line interface for retrieving portfolio data
and performing historical analysis via Portfolio Analyst.
"""
import argparse
import json
import sys
from typing import List, Optional
from .core import PortfolioManager

def main():
    """
    Main entry point for the ibkr_portfolio CLI.
    """
    parser = argparse.ArgumentParser(description="IBKR Portfolio and Portfolio Analyst Tool")
    subparsers = parser.add_subparsers(dest="command", help="Portfolio commands")

    # Command: accounts
    subparsers.add_parser("accounts", help="List portfolio accounts")

    # Command: summary
    summary_parser = subparsers.add_parser("summary", help="Get portfolio summary for an account")
    summary_parser.add_argument("--account", required=True, help="Account ID")

    # Command: ledger
    ledger_parser = subparsers.add_parser("ledger", help="Get portfolio ledger for an account")
    ledger_parser.add_argument("--account", required=True, help="Account ID")

    # Command: positions
    positions_parser = subparsers.add_parser("positions", help="Get portfolio positions for an account")
    positions_parser.add_argument("--account", required=True, help="Account ID")
    positions_parser.add_argument("--page", type=int, default=0, help="Page number for pagination (default: 0)")

    # Command: invalidate
    subparsers.add_parser("invalidate", help="Invalidate portfolio positions cache")

    # Command: allocation
    allocation_parser = subparsers.add_parser("allocation", help="Get portfolio allocation data")
    allocation_parser.add_argument("--account", help="Optional Account ID (if omitted, results for all accounts)")

    # Command: performance
    perf_parser = subparsers.add_parser("performance", help="Get PA performance data")
    perf_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")
    perf_parser.add_argument("--freq", default="D", choices=["D", "M", "Q", "Y"], 
                             help="Frequence: D (Daily), M (Monthly), Q (Quarterly), Y (Yearly). Default: D")

    # Command: pa-summary
    pa_sum_parser = subparsers.add_parser("pa-summary", help="Get PA summary data")
    pa_sum_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")

    # Command: transactions
    trans_parser = subparsers.add_parser("transactions", help="Get PA transactions data")
    trans_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")
    trans_parser.add_argument("--conid", type=int, help="Optional contract ID filter")
    trans_parser.add_argument("--days", type=int, help="Optional number of days to look back")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = PortfolioManager()

    try:
        if args.command == "accounts":
            result = manager.list_accounts()
            print(result.model_dump_json(indent=2))

        elif args.command == "summary":
            result = manager.get_summary(args.account)
            print(result.model_dump_json(indent=2))

        elif args.command == "ledger":
            result = manager.get_ledger(args.account)
            print(result.model_dump_json(indent=2))

        elif args.command == "positions":
            result = manager.get_positions(args.account, args.page)
            print(result.model_dump_json(indent=2))

        elif args.command == "invalidate":
            result = manager.invalidate_positions()
            print(json.dumps(result, indent=2))

        elif args.command == "allocation":
            result = manager.get_allocation(args.account)
            print(result.model_dump_json(indent=2))

        elif args.command == "performance":
            result = manager.get_performance(args.accounts, args.freq)
            print(result.model_dump_json(indent=2))

        elif args.command == "pa-summary":
            result = manager.get_pa_summary(args.accounts)
            print(result.model_dump_json(indent=2))

        elif args.command == "transactions":
            result = manager.get_transactions(args.accounts, args.conid, args.days)
            print(result.model_dump_json(indent=2))

    except Exception as e:
        # Errors are already logged in core.py via IBKRLogger
        sys.exit(1)

if __name__ == "__main__":
    main()
