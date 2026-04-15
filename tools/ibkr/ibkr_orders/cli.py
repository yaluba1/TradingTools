"""
CLI interface for the IBKR Orders tool.
Provides commands to manage the lifecycle of orders directly from the terminal.
"""
import argparse
import json
import sys
from .core import OrdersManager
from ..schemas.order_schemas import OrderRequest

def main():
    """
    Main entry point for the IBKR Orders CLI tool.
    
    This tool provides several subcommands for managing the lifecycle of orders:
    
    * **place**: Place a new order. Requires --account, --conid, --side, --type, --qty.
    * **modify**: Modify an existing order. Requires --account, --cid, --conid, --type, --qty.
    * **cancel**: Cancel a live order. Requires --account, --cid.
    * **list**: List live orders with optional filtering and table output.
    * **sync**: Synchronize the local database with the current IBKR state.
    * **status**: Get detailed status of a single order.
    * **questions**: List pending IBKR questions/prompts.
    * **reply**: Reply to a specific question ID.
    * **background-sync**: Run a continuous synchronization loop.
    """
    parser = argparse.ArgumentParser(
        description="IBKR Orders Management Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Place Order
    place_parser = subparsers.add_parser("place", help="Place a new order")
    place_parser.add_argument("--account", required=True, help="IBKR Account ID")
    place_parser.add_argument("--conid", type=int, required=True, help="Contract ID")
    place_parser.add_argument("--side", choices=["BUY", "SELL"], required=True, help="Order side")
    place_parser.add_argument("--type", required=True, help="Order type (LMT, MKT, STP)")
    place_parser.add_argument("--qty", type=float, required=True, help="Quantity")
    place_parser.add_argument("--price", type=float, help="Limit price")
    place_parser.add_argument("--aux", type=float, help="Aux/Stop price")
    place_parser.add_argument("--tif", default="DAY", help="Time in force")
    place_parser.add_argument("--auto-confirm", action="store_true", help="Automatically accept IBKR warnings/questions")
    place_parser.add_argument("--cid", help="Optional customer order ID")

    # Modify Order
    modify_parser = subparsers.add_parser("modify", help="Modify an existing order")
    modify_parser.add_argument("--account", required=True, help="IBKR Account ID")
    modify_parser.add_argument("--cid", required=True, help="Customer Order ID (cId)")
    modify_parser.add_argument("--conid", type=int, required=True, help="Contract ID")
    modify_parser.add_argument("--type", required=True, help="Order type")
    modify_parser.add_argument("--qty", type=float, required=True, help="Quantity")
    modify_parser.add_argument("--price", type=float, help="Limit price")
    modify_parser.add_argument("--aux", type=float, help="Stop price")
    modify_parser.add_argument("--tif", default="DAY", help="Time in force")

    # Cancel Order
    cancel_parser = subparsers.add_parser("cancel", help="Cancel an order")
    cancel_parser.add_argument("--account", required=True, help="IBKR Account ID")
    cancel_parser.add_argument("--cid", required=True, help="Customer Order ID")

    # Sync
    sync_parser = subparsers.add_parser("sync", help="Synchronize orders with IBKR")
    sync_parser.add_argument("--account", help="Optional specific Account ID")

    # List (Monitoring)
    list_parser = subparsers.add_parser("list", help="List live orders (monitoring)")
    list_parser.add_argument("--account", help="Optional specific Account ID")
    list_parser.add_argument("--status", help="Optional status filter (e.g., Filled, Submitted)")
    list_parser.add_argument("--table", action="store_true", help="Output as a human-friendly table")

    # Status
    status_parser = subparsers.add_parser("status", help="Get status of a specific order")
    status_parser.add_argument("--id", required=True, help="Order ID (server or customer ID)")

    # Questions
    questions_parser = subparsers.add_parser("questions", help="List active IBKR questions/prompts")
    questions_parser.add_argument("--table", action="store_true", help="Output as a human-friendly table")

    # Background Sync
    bg_sync_parser = subparsers.add_parser("background-sync", help="Run background sync loop")
    bg_sync_parser.add_argument("--interval", type=int, default=60, help="Interval in seconds")
    bg_sync_parser.add_argument("--account", help="Optional specific Account ID")

    # Reply
    reply_parser = subparsers.add_parser("reply", help="Reply to an IBKR question/confirmation")
    reply_parser.add_argument("--id", required=True, help="Reply ID from IBKR")
    reply_parser.add_argument("--confirm", choices=["yes", "no"], default="yes", help="Confirmation")

    args = parser.parse_args()
    manager = OrdersManager()

    try:
        if args.command == "place":
            request = OrderRequest(
                conid=args.conid,
                orderType=args.type,
                side=args.side,
                quantity=args.qty,
                price=args.price,
                auxPrice=args.aux,
                tif=args.tif,
                cId=args.cid
            )
            results = manager.place_order(args.account, request, auto_confirm=args.auto_confirm)
            print(json.dumps([r.model_dump() for r in results], indent=2))

        elif args.command == "modify":
            request = OrderRequest(
                conid=args.conid,
                orderType=args.type,
                side="BUY",
                quantity=args.qty,
                price=args.price,
                auxPrice=args.aux,
                tif=args.tif,
                cId=args.cid
            )
            results = manager.place_order(args.account, request)
            print(json.dumps([r.model_dump() for r in results], indent=2))

        elif args.command == "cancel":
            result = manager.cancel_order(args.account, args.cid)
            print(json.dumps(result, indent=2))

        elif args.command == "sync":
            results = manager.sync_orders(args.account)
            print(json.dumps([r.model_dump() for r in results], indent=2))

        elif args.command == "list":
            orders = manager.list_live_orders(args.account, args.status)
            if args.table:
                # Header
                print(f"{'Order ID':<10} {'Symbol':<10} {'Side':<6} {'Qty':<8} {'Filled':<8} {'Status':<15} {'Price':<10}")
                print("-" * 75)
                for o in orders:
                    print(f"{str(o.orderId):<10} {o.ticker or 'N/A':<10} {o.side:<6} {o.totalSize:<8} {o.cumFill:<8} {o.status:<15} {o.lmtPrice or o.avgPrice or 0:<10}")
            else:
                print(json.dumps([o.model_dump() for o in orders], indent=2))

        elif args.command == "status":
            result = manager.get_order_status(args.id)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "questions":
            questions = manager.get_questions()
            if args.table:
                print(f"{'ID':<15} {'Content'}")
                print("-" * 50)
                for q in questions:
                    print(f"{q.id:<15} {' | '.join(q.text)}")
            else:
                print(json.dumps([q.model_dump() for q in questions], indent=2))

        elif args.command == "background-sync":
            manager.run_background_sync(interval_seconds=args.interval, account_id=args.account)

        elif args.command == "reply":
            confirmed = args.confirm == "yes"
            results = manager.reply_to_question(args.id, confirmed)
            print(json.dumps([r.model_dump() for r in results], indent=2))

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
