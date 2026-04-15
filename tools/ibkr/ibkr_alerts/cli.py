"""
Command Line Interface (CLI) for the IBKR Alerts tool.
This module provides a parser and handlers for alerts-related commands,
such as list, create, and delete operations.
"""
import argparse
import json
import sys
from typing import List
from .core import AlertsManager
from ..schemas.alert_schemas import AlertCreateRequest, AlertCondition

def main():
    """
    Main entry point for the IBKR Alerts CLI.
    
    This tool provides several subcommands for managing the lifecycle of alerts:
    
    * **list**: Get all alerts for an account. Requires --account.
    * **get**: Detailed configuration of a single alert. Requires --alert_id.
    * **create**: Create or update an alert. Requires --account, --name, --message, --conditions.
    * **activate**: Enable a disabled alert. Requires --account, --alert_id.
    * **deactivate**: Disable an active alert. Requires --account, --alert_id.
    * **delete**: Remove an alert. Requires --account, --alert_id.
    * **get-mta**: Fetch Mobile Trading Assistant info.
    """
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description="IBKR Alerts Tool: Manage your Interactive Brokers triggers.",
        epilog="See the IBKR Web API documentation for advanced condition details."
    )
    # Define subcommands for the tool
    subparsers = parser.add_subparsers(dest="command", help="Alert commands")

    # Command: 'list' - retrieves all alerts for an account
    list_parser = subparsers.add_parser("list", help="List all alerts for a specific account")
    list_parser.add_argument("--account", required=True, help="The account ID (e.g., DU1234567)")

    # Command: 'get' - details of a single alert
    get_parser = subparsers.add_parser("get", help="Retrieve details for a single alert")
    get_parser.add_argument("--alert_id", required=True, type=int, help="The alert (order) ID")

    # Command: 'create' - creates or modifies an alert
    create_parser = subparsers.add_parser("create", help="Create a new alert or update an existing one")
    create_parser.add_argument("--account", required=True, help="Account ID")
    create_parser.add_argument("--name", required=True, help="A unique name for the alert")
    create_parser.add_argument("--message", required=True, help="Notification message text")
    create_parser.add_argument(
        "--conditions", required=True, 
        help="JSON string representation of one or more alert conditions."
    )
    create_parser.add_argument("--repeatable", type=int, default=0, help="Allow alert to repeat (1=yes, 0=no)")
    create_parser.add_argument("--tif", default="GTC", help="Time in Force: GTC or GTD")
    create_parser.add_argument("--expire_time", help="Required for GTD. Format: 'YYYYMMDD-HH:mm:ss'")
    create_parser.add_argument("--outside_rth", type=int, default=0, help="1 to trigger outside RTH")
    create_parser.add_argument("--send_message", type=int, default=1, help="1 to send notifications")
    create_parser.add_argument("--email", help="Destination email address")

    # Command: 'activate' - enables a disabled alert
    activate_parser = subparsers.add_parser("activate", help="Activate a disabled alert")
    activate_parser.add_argument("--account", required=True, help="Account ID")
    activate_parser.add_argument("--alert_id", required=True, type=int, help="Alert ID")

    # Command: 'deactivate' - disables an active alert
    deactivate_parser = subparsers.add_parser("deactivate", help="Disable an active alert")
    deactivate_parser.add_argument("--account", required=True, help="Account ID")
    deactivate_parser.add_argument("--alert_id", required=True, type=int, help="Alert ID")

    # Command: 'delete' - removes an alert
    delete_parser = subparsers.add_parser("delete", help="Permanently delete an alert")
    delete_parser.add_argument("--account", required=True, help="Account ID")
    delete_parser.add_argument("--alert_id", required=True, type=int, help="Alert ID (0 for ALL)")

    # Command: 'get-mta' - get terminal assistant info
    subparsers.add_parser("get-mta", help="Fetch your Mobile Trading Assistant (MTA) info")

    # Parse arguments provided by the user
    args = parser.parse_args()
    
    # If no command is provided, show help and exit.
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Instantiate the business logic manager.
    manager = AlertsManager()

    try:
        # Route to the appropriate AlertsManager method based on the command.
        if args.command == "list":
            alerts = manager.list_alerts(args.account)
            # Output the results as pretty-printed JSON.
            print(json.dumps([a.model_dump() for a in alerts], indent=2))
        
        elif args.command == "get":
            details = manager.get_alert_details(args.alert_id)
            print(details.model_dump_json(indent=2))
        
        elif args.command == "create":
            # Parse the conditions JSON string into objects.
            conditions_data = json.loads(args.conditions)
            if not isinstance(conditions_data, list):
                conditions_data = [conditions_data]
            
            # Convert raw dictionaries into AlertCondition objects.
            conditions = [AlertCondition(**c) for c in conditions_data]
            
            # Prepare the creation request object.
            request = AlertCreateRequest(
                alertName=args.name,
                alertMessage=args.message,
                alertRepeatable=args.repeatable,
                tif=args.tif,
                expireTime=args.expire_time,
                outsideRth=args.outside_rth,
                sendMessage=args.send_message,
                email=args.email,
                conditions=conditions
            )
            response = manager.create_or_modify_alert(args.account, request)
            print(response.model_dump_json(indent=2))
            
        elif args.command == "activate":
            response = manager.activate_deactivate_alert(args.account, args.alert_id, activate=True)
            print(response.model_dump_json(indent=2))
            
        elif args.command == "deactivate":
            response = manager.activate_deactivate_alert(args.account, args.alert_id, activate=False)
            print(response.model_dump_json(indent=2))
            
        elif args.command == "delete":
            response = manager.delete_alert(args.account, args.alert_id)
            print(response.model_dump_json(indent=2))
            
        elif args.command == "get-mta":
            mta_info = manager.get_mta_alert()
            print(json.dumps(mta_info, indent=2))

    except Exception as e:
        # Standard error handling: log the failure and exit with non-zero code.
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
