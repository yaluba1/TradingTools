"""
Mock tests for IBKR Contract tool.
This script tests the ContractManager logic and CLI command-line tool.
"""
import unittest
import sys
import json
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_contract.core import ContractManager

class TestIBKRContract(unittest.TestCase):
    """
    Unit tests for ContractManager using mocked API responses.
    """
    def setUp(self):
        """
        Initialize the test case by patching dependencies.
        """
        self.mock_client_patcher = patch('tools.ibkr.ibkr_contract.core.IBKRClient')
        self.mock_db_patcher = patch('tools.ibkr.common.logger.db_manager')
        
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_db_manager = self.mock_db_patcher.start()
        
        self.mock_client = self.mock_client_class.return_value
        self.manager = ContractManager()

    def tearDown(self):
        """
        Clean up patchers after each test.
        """
        self.mock_client_patcher.stop()
        self.mock_db_patcher.stop()

    def test_search_contracts(self):
        """Test searching for contracts with rich parameters."""
        self.mock_client.post.return_value = [
            {
                "conid": "265598",
                "companyName": "APPLE INC",
                "symbol": "AAPL",
                "description": "NASDAQ",
                "sections": [{"secType": "STK"}]
            }
        ]
        
        res = self.manager.search_contracts("AAPL", secType="STK", name=True, referrer="test")
        self.assertEqual(len(res.root), 1)
        self.assertEqual(res.root[0].symbol, "AAPL")
        self.assertEqual(res.root[0].conid, "265598")
        self.mock_client.post.assert_called_with(
            "/iserver/secdef/search",
            json_data={"symbol": "AAPL", "secType": "STK", "name": True, "referrer": "test"}
        )

    def test_get_contract_details(self):
        """Test retrieving contract details with rich parameters."""
        self.mock_client.get.return_value = [
            {
                "conid": "265598",
                "companyName": "APPLE INC",
                "symbol": "AAPL",
                "secType": "STK",
                "exchange": "SMART",
                "currency": "USD"
            }
        ]
        
        res = self.manager.get_contract_details("265598", sectype="STK", month="OCT24", exchange="SMART", strike=200.0, right="C")
        self.assertEqual(len(res.root), 1)
        self.assertEqual(res.root[0].conid, "265598")
        self.mock_client.get.assert_called_with(
            "/iserver/secdef/info",
            params={"conid": "265598", "sectype": "STK", "month": "OCT24", "exchange": "SMART", "strike": "200.0", "right": "C"}
        )

    def test_get_strikes(self):
        """Test retrieving option strikes."""
        self.mock_client.get.return_value = {
            "call": [200.0, 210.0],
            "put": [200.0, 190.0]
        }
        
        res = self.manager.get_strikes("265598", "OPT", "OCT24", "SMART")
        self.assertEqual(res.call, [200.0, 210.0])
        self.assertEqual(res.put, [200.0, 190.0])
        self.mock_client.get.assert_called_with(
            "/iserver/secdef/strikes",
            params={"conid": "265598", "sectype": "OPT", "month": "OCT24", "exchange": "SMART"}
        )

    def test_get_trading_schedule_conid(self):
        """Test retrieving conid-based trading schedule."""
        self.mock_client.get.return_value = {
            "exchange_time_zone": "America/New_York",
            "schedules": {}
        }
        
        res = self.manager.get_trading_schedule("265598", exchange="NASDAQ")
        self.assertEqual(res.exchange_time_zone, "America/New_York")
        self.mock_client.get.assert_called_with("/contract/trading-schedule", params={"conid": "265598", "exchange": "NASDAQ"})

    def test_get_trading_schedule_by_symbol(self):
        """Test retrieving trading schedule by symbol."""
        self.mock_client.get.return_value = [
            {
                "id": "NASDAQ",
                "tradingScheduleDate": 20241013,
                "sessions": [{"openingTime": "0930", "closingTime": "1600", "prop": "RTH"}],
                "tradingDayOpeningTime": 930,
                "tradingDayClosingTime": 1600
            }
        ]
        
        res = self.manager.get_trading_schedule_by_symbol("AAPL", "STK", "NASDAQ")
        self.assertEqual(len(res.root), 1)
        self.assertEqual(res.root[0].id, "NASDAQ")
        self.mock_client.get.assert_called_with("/trsrv/secdef/schedule", params={"symbol": "AAPL", "assetClass": "STK", "exchange": "NASDAQ"})

    def test_search_contract_rules(self):
        """Test retrieving contract trading rules."""
        self.mock_client.post.return_value = {
            "orderTypes": ["LMT", "MKT"],
            "tifTypes": ["DAY", "GTC"]
        }
        res = self.manager.search_contract_rules(265598, isBuy=True, exchange="SMART")
        self.assertEqual(res.orderTypes, ["LMT", "MKT"])
        self.mock_client.post.assert_called_with("/iserver/contract/rules", json_data={"conid": 265598, "isBuy": True, "exchange": "SMART"})

    def test_get_algos(self):
        """Test retrieving available algo strategies."""
        self.mock_client.get.return_value = {
            "algos": [
                {
                    "id": "Adaptive",
                    "name": "Adaptive Algo",
                    "parameters": [{"id": "urgency", "name": "Urgency", "type": "str"}]
                }
            ]
        }
        res = self.manager.get_algos("265598", addDescription="1", addParams="1", algos="Adaptive")
        self.assertEqual(len(res.algos), 1)
        self.assertEqual(res.algos[0].id, "Adaptive")
        self.mock_client.get.assert_called_with(
            "/iserver/contract/265598/algos",
            params={"addDescription": "1", "addParams": "1", "algos": "Adaptive"}
        )

    def test_get_instrument_info(self):
        """Test retrieving detailed general instrument information."""
        self.mock_client.get.return_value = {
            "conid": 265598,
            "companyName": "APPLE INC",
            "symbol": "AAPL"
        }
        res = self.manager.get_instrument_info("265598")
        self.assertEqual(res.conid, 265598)
        self.assertEqual(res.companyName, "APPLE INC")
        self.mock_client.get.assert_called_with("/iserver/contract/265598/info")

    def test_get_info_and_rules(self):
        """Test retrieving detailed contract information and rules."""
        self.mock_client.get.return_value = {
            "info": {
                "conid": 265598,
                "companyName": "APPLE INC",
                "symbol": "AAPL"
            },
            "rules": {"minSize": 1}
        }
        res = self.manager.get_info_and_rules("265598")
        self.assertEqual(res.info.conid, 265598)
        self.assertEqual(res.rules["minSize"], 1)
        self.mock_client.get.assert_called_with("/iserver/contract/265598/info-and-rules")

    def test_get_currency_pairs(self):
        """Test retrieving currency pairs."""
        self.mock_client.get.return_value = {
            "USD": [{"symbol": "EUR.USD", "conid": 12087792, "ccyPair": "EUR"}]
        }
        res = self.manager.get_currency_pairs("USD")
        self.assertIn("USD", res.root)
        self.assertEqual(res.root["USD"][0].ccyPair, "EUR")
        self.mock_client.get.assert_called_with("/iserver/currency/pairs", params={"currency": "USD"})

    def test_get_exchange_rate(self):
        """Test retrieving currency exchange rates."""
        self.mock_client.get.return_value = {
            "rate": 0.92,
            "source": "USD",
            "target": "EUR"
        }
        res = self.manager.get_exchange_rate("USD", "EUR")
        self.assertEqual(res.rate, 0.92)
        self.mock_client.get.assert_called_with("/iserver/exchangerate", params={"source": "USD", "target": "EUR"})

    def test_get_bond_filters(self):
        """Test retrieving bond criteria filters."""
        self.mock_client.get.return_value = {
            "bondFilters": [
                {
                    "displayText": "Maturity Date",
                    "columnId": 27,
                    "options": [
                        {"text": "Dec 2028", "value": "202812"}
                    ]
                }
            ]
        }
        res = self.manager.get_bond_filters("US-TREASURY", "BOND")
        self.assertEqual(len(res.bondFilters), 1)
        self.assertEqual(res.bondFilters[0].displayText, "Maturity Date")
        self.mock_client.get.assert_called_with("/iserver/secdef/bond-filters", params={"symbol": "BOND", "issuerId": "US-TREASURY"})

    def test_get_all_conids_by_exchange(self):
        """Test retrieving stock conids by exchange."""
        self.mock_client.get.return_value = [
            {"ticker": "AAPL", "conid": 123, "exchange": "NASDAQ"},
            {"ticker": "MSFT", "conid": 456, "exchange": "NASDAQ"}
        ]
        res = self.manager.get_all_conids_by_exchange("NASDAQ")
        self.assertEqual(res.root[0].conid, 123)
        self.mock_client.get.assert_called_with("/trsrv/all-conids", params={"exchange": "NASDAQ"})

    def test_search_futures_by_symbol(self):
        """Test retrieving futures by symbol."""
        self.mock_client.get.return_value = {
            "ES": [{"symbol": "ES", "conid": 12345, "underlyingConid": 11004968, "expirationDate": 20241220}]
        }
        res = self.manager.search_futures_by_symbol("ES")
        self.assertIn("ES", res.root)
        self.assertEqual(res.root["ES"][0].conid, 12345)
        self.mock_client.get.assert_called_with("/trsrv/futures", params={"symbols": "ES"})

    def test_get_instrument_definition(self):
        """Test retrieving instrument definitions."""
        self.mock_client.get.return_value = {
            "secdef": [
                {"conid": 265598, "symbol": "AAPL", "secType": "STK", "exchange": "NASDAQ", "currency": "USD"}
            ]
        }
        res = self.manager.get_instrument_definition("265598")
        self.assertEqual(len(res.secdef), 1)
        self.assertEqual(res.secdef[0].symbol, "AAPL")
        self.mock_client.get.assert_called_with("/trsrv/secdef", params={"conids": "265598"})

    def test_search_stocks_by_symbol(self):
        """Test retrieving stocks by symbols."""
        self.mock_client.get.return_value = {
            "AAPL": [{"conid": 265598, "symbol": "AAPL", "exchange": "NASDAQ", "currency": "USD"}]
        }
        res = self.manager.search_stocks_by_symbol("AAPL")
        self.assertIn("AAPL", res.root)
        self.assertEqual(res.root["AAPL"][0].conid, 265598)
        self.mock_client.get.assert_called_with("/trsrv/stocks", params={"symbols": "AAPL"})

    def test_get_forecast_categories(self):
        """Test retrieving forecast category tree."""
        self.mock_client.get.return_value = {
            "categories": {
                "politics": {
                    "name": "Politics",
                    "parent_id": "root",
                    "is_restricted": False,
                    "markets": [
                        {
                            "name": "US Presidential Election",
                            "symbol": "PRES.ELECTION",
                            "exchange": "FORECAST",
                            "is_restricted": False,
                            "conid": 848765505,
                            "product_conid": 848765506
                        }
                    ]
                }
            }
        }
        res = self.manager.get_forecast_categories()
        self.assertIn("politics", res.categories)
        self.assertEqual(res.categories["politics"].name, "Politics")
        self.assertEqual(res.categories["politics"].markets[0].conid, 848765505)
        self.mock_client.get.assert_called_with("/forecast/category/tree")

    def test_get_forecast_contract_details(self):
        """Test retrieving forecast contract details."""
        self.mock_client.get.return_value = {
            "conid_yes": 849540484,
            "conid_no": 849540485,
            "question": "Will Jeff Crank win?",
            "side": "Y",
            "strike": 0.5,
            "exchange": "FORECAST",
            "expiration": "20261103",
            "symbol": "CRANK.WIN"
        }
        res = self.manager.get_forecast_contract_details(849540484)
        self.assertEqual(res.conid_yes, 849540484)
        self.assertEqual(res.question, "Will Jeff Crank win?")
        self.mock_client.get.assert_called_with("/forecast/contract/details", params={"conid": 849540484})

    def test_get_forecast_market(self):
        """Test retrieving forecast market outcomes."""
        self.mock_client.get.return_value = {
            "market_name": "US Presidential Election",
            "exchange": "FORECAST",
            "symbol": "PRES.ELECTION",
            "contracts": [
                {
                    "conid": 849540484,
                    "side": "Y",
                    "expiration": "20261103",
                    "strike": 0.5,
                    "underlying_conid": 848765505
                }
            ]
        }
        res = self.manager.get_forecast_market(848765505)
        self.assertEqual(res.market_name, "US Presidential Election")
        self.assertEqual(res.contracts[0].conid, 849540484)
        self.mock_client.get.assert_called_with("/forecast/contract/market", params={"underlyingConid": 848765505})

    def test_get_forecast_rules(self):
        """Test retrieving forecast contract trading rules."""
        self.mock_client.get.return_value = {
            "asset_class": "FORECAST",
            "description": "Election outcome rules",
            "market_name": "US Presidential Election",
            "measured_period": "2026 Election",
            "source_agency": "FEC",
            "price_increments": [
                {"lower_edge": "0.0", "increment": "0.01"}
            ]
        }
        res = self.manager.get_forecast_rules(849540484)
        self.assertEqual(res.asset_class, "FORECAST")
        self.assertEqual(res.price_increments[0].increment, "0.01")
        self.mock_client.get.assert_called_with("/forecast/contract/rules", params={"conid": 849540484})

    def test_get_forecast_schedules(self):
        """Test retrieving forecast trading schedules."""
        self.mock_client.get.return_value = {
            "timezone": "America/New_York",
            "trading_schedules": [
                {
                    "day_of_week": "Monday",
                    "trading_times": [
                        {"open": "0900", "close": "1700"}
                    ]
                }
            ]
        }
        res = self.manager.get_forecast_schedules(849540484)
        self.assertEqual(res.timezone, "America/New_York")
        self.assertEqual(res.trading_schedules[0].day_of_week, "Monday")
        self.mock_client.get.assert_called_with("/forecast/contract/schedules", params={"conid": 849540484})


class TestIBKRContractCLI(unittest.TestCase):
    """
    Unit tests for the CLI interface.
    """
    def setUp(self):
        self.manager_patcher = patch('tools.ibkr.ibkr_contract.cli.ContractManager')
        self.mock_manager = self.manager_patcher.start()
        self.manager_instance = self.mock_manager.return_value
        
    def tearDown(self):
        self.manager_patcher.stop()

    def test_cli_search(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.search_contracts.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'search', '--symbol', 'AAPL', '--sectype', 'STK', '--name', '--referrer', 'test']):
            main()
            self.manager_instance.search_contracts.assert_called_with('AAPL', secType='STK', name=True, referrer='test')

    def test_cli_details(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_contract_details.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'details', '--conid', '265598', '--sectype', 'STK', '--month', 'OCT24', '--exchange', 'SMART', '--strike', '200', '--right', 'C']):
            main()
            self.manager_instance.get_contract_details.assert_called_with('265598', sectype='STK', month='OCT24', exchange='SMART', strike=200.0, right='C')

    def test_cli_strikes(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_strikes.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'strikes', '--conid', '265598', '--sectype', 'OPT', '--month', 'OCT24', '--exchange', 'AMEX']):
            main()
            self.manager_instance.get_strikes.assert_called_with('265598', 'OPT', 'OCT24', 'AMEX')

    def test_cli_schedule(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_trading_schedule.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'schedule', '--conid', '265598', '--exchange', 'NASDAQ']):
            main()
            self.manager_instance.get_trading_schedule.assert_called_with('265598', 'NASDAQ')

    def test_cli_schedule_by_symbol(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_trading_schedule_by_symbol.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'schedule-by-symbol', '--symbol', 'AAPL', '--sectype', 'STK', '--exchange', 'NASDAQ']):
            main()
            self.manager_instance.get_trading_schedule_by_symbol.assert_called_with('AAPL', 'STK', 'NASDAQ')

    def test_cli_rules(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.search_contract_rules.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'rules', '--conid', '265598', '--exchange', 'SMART']):
            main()
            self.manager_instance.search_contract_rules.assert_called_with(265598, True, 'SMART')

    def test_cli_algos(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_algos.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'algos', '--conid', '265598', '--add-description', '1', '--add-params', '1', '--algos', 'Adaptive']):
            main()
            self.manager_instance.get_algos.assert_called_with('265598', '1', '1', 'Adaptive')

    def test_cli_info(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_instrument_info.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'info', '--conid', '265598']):
            main()
            self.manager_instance.get_instrument_info.assert_called_with('265598')

    def test_cli_info_and_rules(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_info_and_rules.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'info-and-rules', '--conid', '265598']):
            main()
            self.manager_instance.get_info_and_rules.assert_called_with('265598')

    def test_cli_currency_pairs(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_currency_pairs.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'currency-pairs', '--currency', 'USD']):
            main()
            self.manager_instance.get_currency_pairs.assert_called_with('USD')

    def test_cli_exchange_rate(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_exchange_rate.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'exchange-rate', '--source', 'USD', '--target', 'EUR']):
            main()
            self.manager_instance.get_exchange_rate.assert_called_with('USD', 'EUR')

    def test_cli_bond_filters(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_bond_filters.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'bond-filters', '--issuer-id', 'US-TREASURY', '--symbol', 'BOND']):
            main()
            self.manager_instance.get_bond_filters.assert_called_with('US-TREASURY', 'BOND')

    def test_cli_all_conids(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_all_conids_by_exchange.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'all-conids', '--exchange', 'NASDAQ']):
            main()
            self.manager_instance.get_all_conids_by_exchange.assert_called_with('NASDAQ')

    def test_cli_futures(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.search_futures_by_symbol.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'futures', '--symbols', 'ES']):
            main()
            self.manager_instance.search_futures_by_symbol.assert_called_with('ES')

    def test_cli_secdef(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.get_instrument_definition.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'secdef', '--conids', '265598']):
            main()
            self.manager_instance.get_instrument_definition.assert_called_with('265598')

    def test_cli_stocks(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {"root": []}
        self.manager_instance.search_stocks_by_symbol.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'stocks', '--symbols', 'AAPL']):
            main()
            self.manager_instance.search_stocks_by_symbol.assert_called_with('AAPL')

    def test_cli_forecast_categories(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_forecast_categories.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'forecast-categories']):
            main()
            self.manager_instance.get_forecast_categories.assert_called_once()

    def test_cli_forecast_details(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_forecast_contract_details.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'forecast-details', '--conid', '849540484']):
            main()
            self.manager_instance.get_forecast_contract_details.assert_called_with(849540484)

    def test_cli_forecast_market(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_forecast_market.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'forecast-market', '--underlying-conid', '848765505']):
            main()
            self.manager_instance.get_forecast_market.assert_called_with(848765505)

    def test_cli_forecast_rules(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_forecast_rules.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'forecast-rules', '--conid', '849540484']):
            main()
            self.manager_instance.get_forecast_rules.assert_called_with(849540484)

    def test_cli_forecast_schedules(self):
        from tools.ibkr.ibkr_contract.cli import main
        mock_res = MagicMock()
        mock_res.model_dump.return_value = {}
        self.manager_instance.get_forecast_schedules.return_value = mock_res
        with patch('sys.argv', ['ibkr_contract', 'forecast-schedules', '--conid', '849540484']):
            main()
            self.manager_instance.get_forecast_schedules.assert_called_with(849540484)

if __name__ == "__main__":
    unittest.main()
