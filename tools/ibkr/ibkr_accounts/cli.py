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

    # Command: 'search' - searches for dynamic accounts by pattern
    search_parser = subparsers.add_parser("search", help="Search for dynamic accounts by a specified pattern")
    search_parser.add_argument("--pattern", required=True, help="The pattern to use for searching accounts (e.g., \"U123*\")")

    # Command: 'summary' - retrieves a summary of account values for a specific account
    summary_parser = subparsers.add_parser("summary", help="Retrieve a summary of account values for a specific account")
    summary_parser.add_argument("--account", required=True, help="The account ID (e.g., U1234567)")

    # Command: \'funds\' - retrieves a summary of available funds for a specific account
    funds_parser = subparsers.add_parser("funds", help="Retrieve a summary of available funds for a specific account")
    funds_parser.add_argument("--account", required=True, help="The account ID (e.g., U1234567)")

    # Command: \"balances\" - retrieves a summary of account balances for a specific account
    balances_parser = subparsers.add_parser("balances", help="Retrieve a summary of account balances for a specific account")
    balances_parser.add_argument("--account", required=True, help="The account ID (e.g., U1234567)")

    # Command: \"margins\" - retrieves a summary of account margin usage for a specific account
    margins_parser = subparsers.add_parser("margins", help="Retrieve a summary of account margin usage for a specific account")
    margins_parser.add_argument("--account", required=True, help="The account ID (e.g., U1234567)")

    # Command: \"market_value\" - retrieves a summary of account market value for a specific account
    market_value_parser = subparsers.add_parser("market_value", help="Retrieve a summary of account market value for a specific account")
    market_value_parser.add_argument("--account", required=True, help="The account ID (e.g., U1234567)")

    # Command: \"set_active\" - sets the active dynamic account for the session
    set_active_parser = subparsers.add_parser("set_active", help="Set a specific account as the active dynamic account for the session")
    set_active_parser.add_argument("--account", required=True, help="The account ID to set as the active dynamic account (e.g., U1234567)")

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

        elif args.command == "search":
            accounts_data = manager.search_dynamic_accounts(args.pattern)
            print(accounts_data.model_dump_json(indent=2))

        elif args.command == "summary":
            account_summary = manager.get_account_summary(args.account)
            print(account_summary.model_dump_json(indent=2))

        elif args.command == "funds":
            available_funds = manager.get_available_funds(args.account)
            print(available_funds.model_dump_json(indent=2))

        elif args.command == "balances":
            account_balances = manager.get_account_balances(args.account)
            print(account_balances.model_dump_json(indent=2))

        elif args.command == "margins":
            margin_summary = manager.get_margin_summary(args.account)
            print(margin_summary.model_dump_json(indent=2))

        elif args.command == "market_value":
            market_value_summary = manager.get_market_value_summary(args.account)
            print(market_value_summary.model_dump_json(indent=2))

        elif args.command == "set_active":
            dynamic_account_response = manager.set_dynamic_account(args.account)
            print(dynamic_account_response.model_dump_json(indent=2))

    except Exception as e:
        # Standard error handling: log the failure and exit with non-zero code.
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
