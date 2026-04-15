"""
CLI interface for the IBKR Session tool.
This module provides the command-line interface for managing and tracking
IBKR Web API sessions.
"""
import argparse
import sys
import json
from .core import SessionManager

def main():
    """
    Main entry point for the ibkr_session CLI.
    """
    parser = argparse.ArgumentParser(description="IBKR Session Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Session commands")

    # Command: status
    subparsers.add_parser("status", help="Check current authentication and connection status")

    # Command: init
    subparsers.add_parser("init", help="Initialize the brokerage session (requires authentication)")

    # Command: logout
    subparsers.add_parser("logout", help="Terminate the current session")

    # Command: tickle
    subparsers.add_parser("tickle", help="Send a heartbeat to keep the session alive")

    # Command: reauth
    subparsers.add_parser("reauth", help="Trigger session re-authentication")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = SessionManager()

    try:
        if args.command == "status":
            result = manager.get_status()
            print(result.model_dump_json(indent=2))

        elif args.command == "init":
            result = manager.init_session()
            print(json.dumps(result, indent=2))

        elif args.command == "logout":
            result = manager.logout()
            print(json.dumps(result, indent=2))

        elif args.command == "tickle":
            result = manager.tickle()
            print(result.model_dump_json(indent=2))

        elif args.command == "reauth":
            result = manager.reauthenticate()
            print(json.dumps(result, indent=2))

    except Exception as e:
        # Errors are logged in core.py via IBKRLogger
        sys.exit(1)

if __name__ == "__main__":
    main()
