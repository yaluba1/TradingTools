"""
CLI interface for the IBKR Scanner tool.
This module provides the command-line interface for market scanning on IBKR.
"""
import argparse
import sys
import json
from .core import ScannerManager

def main():
    """
    Main entry point for the ibkr_scanner CLI.
    """
    parser = argparse.ArgumentParser(description="IBKR Market Scanner Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Scanner commands")

    # Command: params
    subparsers.add_parser("params", help="Retrieve and show valid scanner parameters (15-min limit)")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute a market scan")
    run_parser.add_argument("--instrument", required=True, 
                          help="Asset class code (e.g., STK, FUT, OPT, IND)")
    run_parser.add_argument("--type", required=True, 
                          help="Scanner parameter type (e.g., MOST_ACTIVE, HOT_BY_VOLUME, TOP_GAINERS)")
    run_parser.add_argument("--location", required=True, 
                          help="Exchange/Location code (e.g., STK.US, STK.US.MAJOR, FUT.US)")

    # Simplified filters
    run_parser.add_argument("--price-min", type=float, help="Minimum price filter")
    run_parser.add_argument("--price-max", type=float, help="Maximum price filter")
    run_parser.add_argument("--volume-min", type=int, help="Minimum volume filter")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = ScannerManager()

    try:
        if args.command == "params":
            result = manager.get_params()
            print(result.model_dump_json(indent=2, by_alias=True))

        elif args.command == "run":
            filters = []
            if args.price_min is not None:
                filters.append({"code": "priceAbove", "value": args.price_min})
            if args.price_max is not None:
                filters.append({"code": "priceBelow", "value": args.price_max})
            if args.volume_min is not None:
                filters.append({"code": "volumeAbove", "value": args.volume_min})

            result = manager.run_scan(
                instrument=args.instrument,
                scan_type=args.type,
                location=args.location,
                filters=filters
            )
            print(result.model_dump_json(indent=2))

    except Exception as e:
        # Errors are already logged in core.py via IBKRLogger
        sys.exit(1)

if __name__ == "__main__":
    main()
