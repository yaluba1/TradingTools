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
    positions_parser.add_argument("--page", type=int, help="Optional page number for pagination")

    # Command: positions-nocache
    positions_nocache_parser = subparsers.add_parser("positions-nocache", help="Get near-real-time (uncached) portfolio positions for an account")
    positions_nocache_parser.add_argument("--account", required=True, help="Account ID")
    positions_nocache_parser.add_argument("--model", help="Optional model portfolio code to compare against")
    positions_nocache_parser.add_argument("--sort", help="Optional column name to sort the table by")
    positions_nocache_parser.add_argument("--direction", choices=["a", "d"], help="Optional sort direction: 'a' (ascending) or 'd' (descending)")

    # Command: subaccounts
    subparsers.add_parser("subaccounts", help="List portfolio sub-accounts")

    # Command: positions-conid
    positions_conid_parser = subparsers.add_parser("positions-conid", help="Get positions across all accounts for a specific contract ID")
    positions_conid_parser.add_argument("--conid", type=int, required=True, help="Contract ID")

    # Command: meta
    meta_parser = subparsers.add_parser("meta", help="Get metadata/attributes for an account")
    meta_parser.add_argument("--account", required=True, help="Account ID")

    # Command: position
    position_parser = subparsers.add_parser("position", help="Get portfolio position detail for a conid")
    position_parser.add_argument("--account", required=True, help="Account ID")
    position_parser.add_argument("--conid", type=int, required=True, help="Contract ID")

    # Command: pa-allocation
    pa_alloc_parser = subparsers.add_parser("pa-allocation", help="Get PA consolidated allocation data")
    pa_alloc_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")
    pa_alloc_parser.add_argument("--type", required=True, choices=["ALL", "ASSET_CLASS", "COUNTRY", "FINANCIAL_INSTRUMENT", "REGION", "SECTOR"],
                                 help="Allocation category: ALL, ASSET_CLASS, COUNTRY, FINANCIAL_INSTRUMENT, REGION, SECTOR")
    pa_alloc_parser.add_argument("--currency", help="Optional base currency filter (e.g., USD, EUR)")
    pa_alloc_parser.add_argument("--date", help="Optional reporting date (e.g., 20260613)")
    pa_alloc_parser.add_argument("--model", help="Optional model identifier")

    # Command: invalidate
    invalidate_parser = subparsers.add_parser("invalidate", help="Invalidate portfolio positions cache")
    invalidate_parser.add_argument("--account", required=True, help="Account ID")

    # Command: allocation
    allocation_parser = subparsers.add_parser("allocation", help="Get portfolio allocation data")
    allocation_parser.add_argument("--account", help="Optional Account ID (if omitted, results for all accounts)")

    # Command: performance
    perf_parser = subparsers.add_parser("performance", help="Get PA performance data")
    perf_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")
    perf_parser.add_argument("--period", default="12M", choices=["1D", "7D", "MTD", "1M", "3M", "6M", "12M", "YTD"], 
                             help="Period: 1D, 7D, MTD, 1M, 3M, 6M, 12M, YTD. Default: 12M")

    # Command: performance-all
    perf_all_parser = subparsers.add_parser("performance-all", help="Get PA performance data for all periods")
    perf_all_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")

    # Command: pa-summary
    pa_sum_parser = subparsers.add_parser("pa-summary", help="Get PA summary data")
    pa_sum_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")

    # Command: transactions
    trans_parser = subparsers.add_parser("transactions", help="Get PA transactions data")
    trans_parser.add_argument("--accounts", required=True, nargs="+", help="One or more Account IDs")
    trans_parser.add_argument("--conids", required=True, type=int, nargs="+", help="One or more Contract IDs")
    trans_parser.add_argument("--currency", required=True, help="Currency code (e.g. USD)")
    trans_parser.add_argument("--days", type=int, default=90, help="Number of days to look back (default: 90)")

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
            # If page is not specified, it will be None
            page = getattr(args, "page", None)
            result = manager.get_positions(args.account, page)
            print(result.model_dump_json(indent=2))

        elif args.command == "positions-nocache":
            model = getattr(args, "model", None)
            sort = getattr(args, "sort", None)
            direction = getattr(args, "direction", None)
            result = manager.get_positions_nocache(
                account_id=args.account,
                model=model,
                sort=sort,
                direction=direction
            )
            print(result.model_dump_json(indent=2))

        elif args.command == "subaccounts":
            result = manager.list_subaccounts()
            print(result.model_dump_json(indent=2))

        elif args.command == "positions-conid":
            result = manager.get_positions_by_conid(args.conid)
            print(result.model_dump_json(indent=2))

        elif args.command == "meta":
            result = manager.get_account_meta(args.account)
            print(result.model_dump_json(indent=2))

        elif args.command == "position":
            result = manager.get_position_by_conid(args.account, args.conid)
            print(result.model_dump_json(indent=2))

        elif args.command == "pa-allocation":
            result = manager.get_pa_allocation(
                account_ids=args.accounts,
                type=args.type,
                currency=args.currency,
                date=args.date,
                model=args.model
            )
            print(result.model_dump_json(indent=2))

        elif args.command == "invalidate":
            result = manager.invalidate_positions(args.account)
            print(json.dumps(result, indent=2))

        elif args.command == "allocation":
            result = manager.get_allocation(args.account)
            print(result.model_dump_json(indent=2))

        elif args.command == "performance":
            result = manager.get_performance(args.accounts, args.period)
            print(result.model_dump_json(indent=2))

        elif args.command == "performance-all":
            result = manager.get_performance_all_periods(args.accounts)
            print(result.model_dump_json(indent=2))

        elif args.command == "pa-summary":
            result = manager.get_pa_summary(args.accounts)
            print(result.model_dump_json(indent=2))

        elif args.command == "transactions":
            result = manager.get_transactions(
                account_ids=args.accounts,
                conids=args.conids,
                currency=args.currency,
                days=args.days
            )
            print(result.model_dump_json(indent=2))

    except Exception as e:
        # Check if the exception contains a response with JSON error message from the server
        error_msg = str(e)
        import requests
        if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
            try:
                err_data = e.response.json()
                if isinstance(err_data, dict) and "error" in err_data:
                    error_msg = err_data["error"]
                elif isinstance(err_data, dict) and "message" in err_data:
                    error_msg = err_data["message"]
            except Exception:
                pass
        
        # Standard error handling: log the failure and exit with non-zero code.
        print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
