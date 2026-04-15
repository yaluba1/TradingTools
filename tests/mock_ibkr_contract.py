"""
Mock tests for IBKR Contract tool.
This script tests the ContractManager logic by mocking the IBKRClient.
"""
import unittest
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
        # Patch IBKRClient and DatabaseManager to avoid real network/DB calls.
        # Although DB logging is disabled for contracts, the logger still initializes it.
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
        """
        Test searching for contracts by symbol.
        """
        # Mock Response for /iserver/secdef/search
        self.mock_client.post.return_value = [
            {
                "conid": "265598",
                "companyName": "APPLE INC",
                "symbol": "AAPL",
                "description": "NASDAQ",
                "sections": [{"secType": "STK"}]
            }
        ]
        
        res = self.manager.search_contracts("AAPL")
        self.assertEqual(len(res.root), 1)
        self.assertEqual(res.root[0].symbol, "AAPL")
        self.assertEqual(res.root[0].conid, "265598")
        self.mock_client.post.assert_called_with("/iserver/secdef/search", json_data={"symbol": "AAPL"})

    def test_get_contract_details(self):
        """
        Test retrieving contract details by conid.
        """
        # Mock Response for /iserver/secdef/info
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
        
        res = self.manager.get_contract_details("265598")
        self.assertEqual(len(res.root), 1)
        self.assertEqual(res.root[0].conid, "265598")
        self.assertEqual(res.root[0].secType, "STK")
        self.mock_client.get.assert_called_with("/iserver/secdef/info", params={"conid": "265598", "sectype": "STK"})

    def test_get_strikes(self):
        """
        Test retrieving option strikes.
        """
        # Mock Response for /iserver/secdef/strikes
        self.mock_client.get.return_value = {
            "call": [200.0, 210.0],
            "put": [200.0, 190.0]
        }
        
        res = self.manager.get_strikes("265598", "OPT", "OCT24")
        self.assertEqual(res.call, [200.0, 210.0])
        self.assertEqual(res.put, [200.0, 190.0])
        self.mock_client.get.assert_called_with(
            "/iserver/secdef/strikes", 
            params={"conid": "265598", "sectype": "OPT", "month": "OCT24", "exchange": "SMART"}
        )

    def test_get_trading_schedule(self):
        """
        Test retrieving trading schedule.
        """
        # Mock Response for /iserver/secdef/tradingschedule
        self.mock_client.get.return_value = [
            {
                "id": "NASDAQ",
                "tradingScheduleDate": 20241013,
                "sessions": [
                    {"openingTime": "0930", "closingTime": "1600", "prop": "RTH"}
                ],
                "tradingDayOpeningTime": 930,
                "tradingDayClosingTime": 1600
            }
        ]
        
        res = self.manager.get_trading_schedule("265598")
        self.assertEqual(len(res.root), 1)
        self.assertEqual(res.root[0].id, "NASDAQ")
        self.assertEqual(res.root[0].tradingScheduleDate, 20241013)
        self.mock_client.get.assert_called_with("/iserver/secdef/tradingschedule", params={"conid": "265598"})

if __name__ == "__main__":
    unittest.main()
