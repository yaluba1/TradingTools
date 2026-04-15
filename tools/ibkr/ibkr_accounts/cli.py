"""
Command Line Interface (CLI) for the IBKR Accounts tool.
This module provides a parser and handlers for account-related commands,
such as listing accounts, fetching PnL, and retrieving ownership info.
"""
import argparse
import json
import sys
from .core import AccountsManager

def main():
    """
    Main entry point for the IBKR Accounts CLI.
    
    This tool provides subcommands for querying account information:
    
    * **list**: List all accessible brokerage accounts and session context.
    * **pnl**: Retrieve Profit and Loss (PnL) data for the current session.
    * **ownership**: Retrieve signature and ownership info for an account. Requires --account.
    """
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="IBKR Accounts Tool: Manage and query your Interactive Brokers accounts.",
        epilog="Note: Context-sensitive endpoints (like orders) require 'list' to be called first."
    )
    # Define subcommands for the tool
    subparsers = parser.add_subparsers(dest="command", help="Account commands")

    # Command: 'list' - retrieves all accessible accounts and validates the session context
    subparsers.add_parser("list", help="List all accessible brokerage accounts and session context")

    # Command: 'pnl' - retrieves partitioned Profit and Loss data
    subparsers.add_parser("pnl", help="Retrieve Profit and Loss (PnL) data for the current session")

    # Command: 'ownership' - retrieves applicant and entity details for a specific account
    owner_parser = subparsers.add_parser("ownership", help="Retrieve signature and ownership info for an account")
    owner_parser.add_argument("--account", required=True, help="The account ID (e.g., U1234567)")

    # Parse arguments provided by the user
    args = parser.parse_args()
    
    # If no command is provided, show help and exit cleanly.
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Instantiate the business logic manager.
    manager = AccountsManager()

    try:
        # Route to the appropriate AccountsManager method based on the command.
        if args.command == "list":
            accounts_data = manager.list_accounts()
            # Output the results as pretty-printed JSON.
            print(accounts_data.model_dump_json(indent=2))
        
        elif args.command == "pnl":
            pnl_data = manager.get_pnl()
            print(pnl_data.model_dump_json(indent=2))
        
        elif args.command == "ownership":
            owner_info = manager.get_signatures_and_owners(args.account)
            print(owner_info.model_dump_json(indent=2))

    except Exception as e:
        # Standard error handling: log the failure and exit with non-zero code.
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
