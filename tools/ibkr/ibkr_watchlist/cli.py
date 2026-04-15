"""
CLI interface for the IBKR Watchlist tool.
This module provides the command-line interface for listing, viewing, and
managing Interactive Brokers watchlists.
"""
import argparse
import sys
import json
from .core import WatchlistManager

def main():
    """
    Main entry point for the ibkr_watchlist CLI.
    """
    parser = argparse.ArgumentParser(description="IBKR Watchlist Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Watchlist commands")

    # Command: list
    subparsers.add_parser("list", help="List all watchlists (User-defined and System)")

    # Command: get
    get_parser = subparsers.add_parser("get", help="Get detail of a specific watchlist")
    get_parser.add_argument("--id", required=True, help="The unique identifier for the watchlist (e.g. USER_123 or SYST_1)")

    # Command: create
    create_parser = subparsers.add_parser("create", help="Create a new user-defined watchlist")
    create_parser.add_argument("--name", required=True, help="Name for the new watchlist")
    create_parser.add_argument("--conids", required=True, type=int, nargs="+", help="Contract IDs to include")

    # Command: delete
    delete_parser = subparsers.add_parser("delete", help="Delete a user-defined watchlist")
    delete_parser.add_argument("--id", required=True, help="The ID of the watchlist to delete")

    # Command: add
    add_parser = subparsers.add_parser("add", help="Add contracts to an existing watchlist")
    add_parser.add_argument("--id", required=True, help="Watchlist ID")
    add_parser.add_argument("--conids", required=True, type=int, nargs="+", help="Contract IDs to add")

    # Command: remove
    remove_parser = subparsers.add_parser("remove", help="Remove contracts from an existing watchlist")
    remove_parser.add_argument("--id", required=True, help="Watchlist ID")
    remove_parser.add_argument("--conids", required=True, type=int, nargs="+", help="Contract IDs to remove")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = WatchlistManager()

    try:
        if args.command == "list":
            result = manager.list_watchlists()
            print(result.model_dump_json(indent=2, by_alias=True))

        elif args.command == "get":
            result = manager.get_watchlist(args.id)
            print(result.model_dump_json(indent=2))

        elif args.command == "create":
            result = manager.create_watchlist(args.name, args.conids)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"Watchlist '{args.name}' created successfully.")

        elif args.command == "delete":
            result = manager.delete_watchlist(args.id)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"Watchlist '{args.id}' deleted successfully.")

        elif args.command == "add":
            result = manager.add_to_watchlist(args.id, args.conids)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"Contracts added to '{args.id}' successfully.")

        elif args.command == "remove":
            result = manager.remove_from_watchlist(args.id, args.conids)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"Contracts removed from '{args.id}' successfully.")

    except Exception as e:
        # Errors are already logged in core.py via IBKRLogger
        sys.exit(1)

if __name__ == "__main__":
    main()
