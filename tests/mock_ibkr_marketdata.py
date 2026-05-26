"""
Mock tests for IBKR Market Data tool.
This script tests the MarketDataManager logic and CLI interface by mocking the IBKRClient.
"""
import unittest
import json
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_marketdata.core import MarketDataManager
from tools.ibkr.schemas.marketdata_schemas import HistoricalDataResponse

class TestIBKRMarketData(unittest.TestCase):
    """
    Unit tests for MarketDataManager using mocked API responses.
    """
    def setUp(self):
        self.mock_client_patcher = patch('tools.ibkr.ibkr_marketdata.core.IBKRClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = self.mock_client_class.return_value
        self.manager = MarketDataManager()

    def tearDown(self):
        self.mock_client_patcher.stop()

    def test_get_historical_data_success(self):
        """Test successfully retrieving historical bar data."""
        self.mock_client.get.return_value = {
            "serverId": "12345",
            "symbol": "AAPL",
            "text": "Apple Inc.",
            "priceFactor": 100,
            "startTime": "20260520-09:30:00",
            "timePeriod": "1d",
            "barLength": 3600,
            "data": [
                {"o": 180.0, "c": 181.5, "h": 182.0, "l": 179.5, "v": 1000.0, "t": 1724864400000}
            ],
            "points": 1
        }
        
        res = self.manager.get_historical_data(conid=265598, period="1d", bar="1h")
        self.assertEqual(res.symbol, "AAPL")
        self.assertEqual(res.points, 1)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].o, 180.0)
        self.mock_client.get.assert_called_with(
            "/iserver/marketdata/history",
            params={"conid": "265598", "period": "1d", "bar": "1h"}
        )

    def test_get_historical_data_optional_params(self):
        """Test retrieving historical bar data with all optional parameters."""
        self.mock_client.get.return_value = {
            "symbol": "MSFT",
            "data": []
        }
        
        res = self.manager.get_historical_data(
            conid=789,
            period="1w",
            bar="1d",
            outsideRth=True,
            barType="midprice",
            startTime="20260501-16:00:00"
        )
        self.assertEqual(res.symbol, "MSFT")
        self.mock_client.get.assert_called_with(
            "/iserver/marketdata/history",
            params={
                "conid": "789",
                "period": "1w",
                "bar": "1d",
                "outsideRth": "true",
                "barType": "midprice",
                "startTime": "20260501-16:00:00"
            }
        )

    def test_get_historical_data_error(self):
        """Test handling of API errors."""
        self.mock_client.get.side_effect = Exception("Gateway Timeout")
        with self.assertRaises(Exception) as ctx:
            self.manager.get_historical_data(conid=265598, period="1d", bar="1h")
        self.assertIn("Gateway Timeout", str(ctx.exception))


class TestIBKRMarketDataCLI(unittest.TestCase):
    """
    Unit tests for the CLI interface of the Market Data tool.
    """
    def setUp(self):
        self.manager_patcher = patch('tools.ibkr.ibkr_marketdata.cli.MarketDataManager')
        self.mock_manager = self.manager_patcher.start()
        self.manager_instance = self.mock_manager.return_value

    def tearDown(self):
        self.manager_patcher.stop()

    def test_cli_no_command(self):
        """Test calling CLI with no commands prints help."""
        from tools.ibkr.ibkr_marketdata.cli import main
        with patch('sys.argv', ['ibkr_marketdata']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

    def test_cli_history_success(self):
        """Test successfully running the history command via CLI."""
        from tools.ibkr.ibkr_marketdata.cli import main
        mock_response = MagicMock(spec=HistoricalDataResponse)
        mock_response.model_dump.return_value = {"symbol": "AAPL", "data": []}
        self.manager_instance.get_historical_data.return_value = mock_response

        with patch('sys.argv', ['ibkr_marketdata', 'history', '--conid', '265598', '--period', '1d', '--bar', '1h']):
            main()
            self.manager_instance.get_historical_data.assert_called_with(
                conid=265598,
                period="1d",
                bar="1h",
                outsideRth=None,
                barType=None,
                startTime=None
            )

    def test_cli_history_optional_args(self):
        """Test running history CLI command with all optional arguments."""
        from tools.ibkr.ibkr_marketdata.cli import main
        mock_response = MagicMock(spec=HistoricalDataResponse)
        mock_response.model_dump.return_value = {"symbol": "AAPL", "data": []}
        self.manager_instance.get_historical_data.return_value = mock_response

        with patch('sys.argv', [
            'ibkr_marketdata', 'history',
            '--conid', '265598',
            '--period', '2d',
            '--bar', '5min',
            '--outside-rth',
            '--bar-type', 'midprice',
            '--start-time', '20260520-09:30:00'
        ]):
            main()
            self.manager_instance.get_historical_data.assert_called_with(
                conid=265598,
                period="2d",
                bar="5min",
                outsideRth=True,
                barType="midprice",
                startTime="20260520-09:30:00"
            )

    def test_cli_history_error(self):
        """Test CLI error handling on manager exception."""
        from tools.ibkr.ibkr_marketdata.cli import main
        self.manager_instance.get_historical_data.side_effect = Exception("API connection failure")

        with patch('sys.argv', ['ibkr_marketdata', 'history', '--conid', '265598', '--period', '1d', '--bar', '1h']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

if __name__ == "__main__":
    unittest.main()
