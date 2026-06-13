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
    
    This tool provides subcommands for querying security contracts and market parameters:
    
    * **search**: Search for contracts by ticker symbol.
    * **details**: Get detailed contract info.
    * **strikes**: Get available option strikes for an underlying.
    * **schedule**: Get trading schedule by ConID.
    * **schedule-by-symbol**: Get trading schedule by ticker symbol.
    * **rules**: Get contract/market trading rules.
    * **algos**: Get available trading algorithms.
    * **info**: Get contract general information.
    * **info-and-rules**: Get combined contract info and rules.
    * **currency-pairs**: Get available FX trading pairs.
    * **exchange-rate**: Get FX exchange rates.
    * **bond-filters**: Get bond criteria and filter options.
    * **all-conids**: List all tradable ConIDs on a specific exchange.
    * **futures**: Search for non-expired futures by symbol.
    * **secdef**: Fetch detailed security definitions for a list of ConIDs.
    * **stocks**: Query stock definitions and ConIDs by symbol.
    * **forecast-categories**: List Event Contract Forecast categories and underlying markets.
    * **forecast-details**: Retrieve details for a specific forecast contract outcome ConID.
    * **forecast-market**: Query all contracts under an underlying market ConID.
    * **forecast-rules**: Retrieve trading rules for a forecast contract ConID.
    * **forecast-schedules**: Retrieve trading schedule for a forecast contract ConID.
    """
    parser = argparse.ArgumentParser(description="IBKR Contract Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search for contracts by symbol")
    search_parser.add_argument("--symbol", required=True, help="Ticker symbol (e.g., AAPL)")
    search_parser.add_argument("--sectype", help="Asset class filter (e.g., STK, OPT, FUT)")
    search_parser.add_argument("--name", action="store_true", help="If set, also search company names")
    search_parser.add_argument("--referrer", help="Referrer source identifier")

    # Details subcommand
    details_parser = subparsers.add_parser("details", help="Get detailed contract info")
    details_parser.add_argument("--conid", required=True, help="Contract ID")
    details_parser.add_argument("--sectype", help="Security type (e.g., STK)")
    details_parser.add_argument("--type", help="Security type alias (backwards-compatible)")
    details_parser.add_argument("--month", help="Contract month (e.g., OCT24)")
    details_parser.add_argument("--exchange", help="Target exchange")
    details_parser.add_argument("--strike", type=float, help="Strike price")
    details_parser.add_argument("--right", help="C or P (for options)")

    # Strikes subcommand
    strikes_parser = subparsers.add_parser("strikes", help="Get available option strikes")
    strikes_parser.add_argument("--conid", required=True, help="Underlying contract ID")
    strikes_parser.add_argument("--sectype", help="Security type (e.g., OPT)")
    strikes_parser.add_argument("--type", help="Security type alias (backwards-compatible)")
    strikes_parser.add_argument("--month", required=True, help="Contract month (e.g., OCT24)")
    strikes_parser.add_argument("--exchange", default="SMART", help="Exchange (default: SMART)")

    # Schedule subcommand (ConID-based)
    schedule_parser = subparsers.add_parser("schedule", help="Get trading schedule by ConID")
    schedule_parser.add_argument("--conid", required=True, help="Contract ID")
    schedule_parser.add_argument("--exchange", help="Exchange")

    # Schedule-by-symbol subcommand
    sbs_parser = subparsers.add_parser("schedule-by-symbol", help="Get trading schedule by symbol")
    sbs_parser.add_argument("--symbol", required=True, help="Ticker symbol")
    sbs_parser.add_argument("--sectype", required=True, help="Security type (e.g., STK)")
    sbs_parser.add_argument("--exchange", help="Exchange")

    # Rules subcommand
    rules_parser = subparsers.add_parser("rules", help="Get contract rules")
    rules_parser.add_argument("--conid", required=True, type=int, help="Contract ID")
    rules_parser.add_argument("--is-buy", action="store_true", default=True, help="Set if buying (default)")
    rules_parser.add_argument("--no-buy", dest="is_buy", action="store_false", help="Set if selling")
    rules_parser.add_argument("--exchange", help="Exchange")

    # Algos subcommand
    algos_parser = subparsers.add_parser("algos", help="Get algos by conid")
    algos_parser.add_argument("--conid", required=True, help="Contract ID")
    algos_parser.add_argument("--add-description", help="Set to 1 to include descriptions")
    algos_parser.add_argument("--add-params", help="Set to 1 to include parameters")
    algos_parser.add_argument("--algos", help="Semicolon-delimited specific algos")

    # Info subcommand
    info_parser = subparsers.add_parser("info", help="Get contract info by conid")
    info_parser.add_argument("--conid", required=True, help="Contract ID")

    # Info-and-rules subcommand
    iar_parser = subparsers.add_parser("info-and-rules", help="Get contract info and rules by conid")
    iar_parser.add_argument("--conid", required=True, help="Contract ID")

    # Currency pairs subcommand
    cp_parser = subparsers.add_parser("currency-pairs", help="Get currency pairs by target currency")
    cp_parser.add_argument("--currency", required=True, help="Base/Target currency (e.g., USD)")

    # Exchange rate subcommand
    er_parser = subparsers.add_parser("exchange-rate", help="Get exchange rate between source and target")
    er_parser.add_argument("--source", required=True, help="Source currency (e.g., USD)")
    er_parser.add_argument("--target", required=True, help="Target currency (e.g., EUR)")

    # Bond filters subcommand
    bf_parser = subparsers.add_parser("bond-filters", help="Get bond filters by issuer id")
    bf_parser.add_argument("--issuer-id", required=True, help="Bond issuer ID")
    bf_parser.add_argument("--symbol", default="BOND", help="Defaults to BOND")

    # All-conids subcommand
    ac_parser = subparsers.add_parser("all-conids", help="Get all stock conids by exchange")
    ac_parser.add_argument("--exchange", required=True, help="Exchange (e.g., NASDAQ)")

    # Futures subcommand
    futures_parser = subparsers.add_parser("futures", help="Get futures by symbols")
    futures_parser.add_argument("--symbols", required=True, help="Comma-separated symbols")

    # Secdef subcommand
    secdef_parser = subparsers.add_parser("secdef", help="Get instrument definition details by conids")
    secdef_parser.add_argument("--conids", required=True, help="Comma-separated conids")

    # Stocks subcommand
    stocks_parser = subparsers.add_parser("stocks", help="Get stocks by symbols")
    stocks_parser.add_argument("--symbols", required=True, help="Comma-separated symbols")

    # Forecast-categories subcommand
    fc_parser = subparsers.add_parser("forecast-categories", help="List forecast categories and markets")

    # Forecast-details subcommand
    fd_parser = subparsers.add_parser("forecast-details", help="Get details for forecast contract")
    fd_parser.add_argument("--conid", required=True, type=int, help="Contract outcome ConID")

    # Forecast-market subcommand
    fm_parser = subparsers.add_parser("forecast-market", help="Get contracts for underlying market")
    fm_parser.add_argument("--underlying-conid", required=True, type=int, help="Underlying market ConID")

    # Forecast-rules subcommand
    fr_parser = subparsers.add_parser("forecast-rules", help="Get rules for forecast contract")
    fr_parser.add_argument("--conid", required=True, type=int, help="Contract outcome ConID")

    # Forecast-schedules subcommand
    fs_parser = subparsers.add_parser("forecast-schedules", help="Get trading schedule for forecast contract")
    fs_parser.add_argument("--conid", required=True, type=int, help="Contract outcome ConID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    manager = ContractManager()

    try:
        if args.command == "search":
            result = manager.search_contracts(
                args.symbol,
                secType=args.sectype,
                name=args.name if args.name else None,
                referrer=args.referrer
            )
            print(json.dumps(result.model_dump(), indent=2))
            
        elif args.command == "details":
            sectype = args.sectype or args.type
            result = manager.get_contract_details(
                args.conid,
                sectype=sectype,
                month=args.month,
                exchange=args.exchange,
                strike=args.strike,
                right=args.right
            )
            print(json.dumps(result.model_dump(), indent=2))
            
        elif args.command == "strikes":
            sectype = args.sectype or args.type or "OPT"
            result = manager.get_strikes(args.conid, sectype, args.month, args.exchange)
            print(json.dumps(result.model_dump(), indent=2))
            
        elif args.command == "schedule":
            result = manager.get_trading_schedule(args.conid, args.exchange)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "schedule-by-symbol":
            result = manager.get_trading_schedule_by_symbol(args.symbol, args.sectype, args.exchange)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "rules":
            result = manager.search_contract_rules(args.conid, args.is_buy, args.exchange)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "algos":
            result = manager.get_algos(args.conid, args.add_description, args.add_params, args.algos)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "info":
            result = manager.get_instrument_info(args.conid)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "info-and-rules":
            result = manager.get_info_and_rules(args.conid)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "currency-pairs":
            result = manager.get_currency_pairs(args.currency)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "exchange-rate":
            result = manager.get_exchange_rate(args.source, args.target)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "bond-filters":
            result = manager.get_bond_filters(args.issuer_id, args.symbol)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "all-conids":
            result = manager.get_all_conids_by_exchange(args.exchange)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "futures":
            result = manager.search_futures_by_symbol(args.symbols)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "secdef":
            result = manager.get_instrument_definition(args.conids)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "stocks":
            result = manager.search_stocks_by_symbol(args.symbols)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "forecast-categories":
            result = manager.get_forecast_categories()
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "forecast-details":
            result = manager.get_forecast_contract_details(args.conid)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "forecast-market":
            result = manager.get_forecast_market(args.underlying_conid)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "forecast-rules":
            result = manager.get_forecast_rules(args.conid)
            print(json.dumps(result.model_dump(), indent=2))

        elif args.command == "forecast-schedules":
            result = manager.get_forecast_schedules(args.conid)
            print(json.dumps(result.model_dump(), indent=2))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
