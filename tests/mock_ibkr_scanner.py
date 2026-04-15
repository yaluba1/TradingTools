"""
Mock tests for IBKR Scanner tool.
This script tests the ScannerManager logic by mocking the IBKRClient.
"""
import unittest
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_scanner.core import ScannerManager

class TestIBKRScanner(unittest.TestCase):
    """
    Unit tests for ScannerManager using mocked API responses.
    """
    def setUp(self):
        self.mock_client_patcher = patch('tools.ibkr.ibkr_scanner.core.IBKRClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = self.mock_client_class.return_value
        self.manager = ScannerManager()

    def tearDown(self):
        self.mock_client_patcher.stop()

    def test_get_params_success(self):
        """Test retrieving scanner parameters."""
        self.mock_client.get.return_value = {
            "scan_type_list": [{"display_name": "Most Active", "code": "MOST_ACTIVE"}],
            "instrument_list": [{"display_name": "Stock", "code": "STK"}],
            "filter_list": [{"display_name": "Price Above", "code": "priceAbove"}],
            "location_tree": [{"display_name": "United States", "type": "STK.US"}]
        }
        res = self.manager.get_params()
        self.assertEqual(len(res.scan_type_list), 1)
        self.assertEqual(res.scan_type_list[0].code, "MOST_ACTIVE")
        self.mock_client.get.assert_called_with("/iserver/scanner/params")

    def test_run_scan_success_object(self):
        """Test executing a scan when API returns an object."""
        self.mock_client.post.return_value = {
            "total": 1, "offset": 0, "limit": 10,
            "results": [{"conid": 265598, "symbol": "AAPL"}]
        }
        res = self.manager.run_scan("STK", "MOST_ACTIVE", "STK.US.MAJOR")
        self.assertEqual(len(res.results), 1)
        self.assertEqual(res.results[0].symbol, "AAPL")
        self.mock_client.post.assert_called_once()

    def test_run_scan_success_list(self):
        """Test executing a scan when API returns a raw list."""
        self.mock_client.post.return_value = [{"conid": 265598, "symbol": "AAPL"}]
        res = self.manager.run_scan("STK", "MOST_ACTIVE", "STK.US.MAJOR")
        self.assertEqual(len(res.results), 1)
        self.mock_client.post.assert_called_once()

    def test_run_scan_with_filters(self):
        """Test executing a scan with filters."""
        self.mock_client.post.return_value = {"total": 0, "offset": 0, "limit": 0, "results": []}
        filters = [{"code": "priceAbove", "value": 100}]
        self.manager.run_scan("STK", "MOST_ACTIVE", "STK.US.MAJOR", filters=filters)
        
        args, kwargs = self.mock_client.post.call_args
        payload = kwargs['json_data']
        self.assertEqual(payload['filter'][0]['code'], "priceAbove")
        self.assertEqual(payload['filter'][0]['value'], 100)

    def test_get_params_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_params()

    def test_run_scan_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.run_scan("STK", "TYPE", "LOC")

class TestIBKRScannerCLI(unittest.TestCase):
    """
    Unit tests for the CLI interface.
    """
    def setUp(self):
        self.manager_patcher = patch('tools.ibkr.ibkr_scanner.cli.ScannerManager')
        self.mock_manager = self.manager_patcher.start()
        self.manager_instance = self.mock_manager.return_value
        
    def tearDown(self):
        self.manager_patcher.stop()

    def test_cli_params(self):
        from tools.ibkr.ibkr_scanner.cli import main
        mock_params = MagicMock()
        # Mock model_dump_json for print
        mock_params.model_dump_json.return_value = "{}"
        self.manager_instance.get_params.return_value = mock_params
        
        with patch('sys.argv', ['ibkr_scanner', 'params']):
            main()
            self.manager_instance.get_params.assert_called_once()

    def test_cli_run_basic(self):
        from tools.ibkr.ibkr_scanner.cli import main
        mock_res = MagicMock()
        mock_res.model_dump_json.return_value = "{}"
        self.manager_instance.run_scan.return_value = mock_res
        
        with patch('sys.argv', ['ibkr_scanner', 'run', '--instrument', 'STK', '--type', 'MA', '--location', 'US']):
            main()
            self.manager_instance.run_scan.assert_called_with(
                instrument='STK', scan_type='MA', location='US', filters=[]
            )

    def test_cli_run_filters(self):
        from tools.ibkr.ibkr_scanner.cli import main
        mock_res = MagicMock()
        mock_res.model_dump_json.return_value = "{}"
        self.manager_instance.run_scan.return_value = mock_res
        
        with patch('sys.argv', ['ibkr_scanner', 'run', '--instrument', 'STK', '--type', 'MA', '--location', 'US', 
                               '--price-min', '10', '--volume-min', '100']):
            main()
            filters = [
                {"code": "priceAbove", "value": 10.0},
                {"code": "volumeAbove", "value": 100}
            ]
            self.manager_instance.run_scan.assert_called_with(
                instrument='STK', scan_type='MA', location='US', filters=filters
            )

if __name__ == "__main__":
    unittest.main()
