"""
Mock tests for IBKR Accounts tool.
This script tests the AccountsManager logic by mocking the IBKRClient.
"""
import unittest
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_accounts.core import AccountsManager

class TestIBKRAccounts(unittest.TestCase):
    """
    Unit tests for AccountsManager using mocked API responses.
    """
    def setUp(self):
        """
        Initialize the test case by patching dependencies.
        """
        # Patch IBKRClient and DatabaseManager to avoid real network/DB calls
        self.mock_client_patcher = patch('tools.ibkr.ibkr_accounts.core.IBKRClient')
        self.mock_db_patcher = patch('tools.ibkr.common.logger.db_manager')
        
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_db_manager = self.mock_db_patcher.start()
        
        self.mock_client = self.mock_client_class.return_value
        self.manager = AccountsManager()

    def tearDown(self):
        """
        Clean up patchers after each test.
        """
        self.mock_client_patcher.stop()
        self.mock_db_patcher.stop()

    def test_list_accounts(self):
        """
        Test retrieving the list of brokerage accounts.
        """
        # Mock Response for /iserver/accounts
        self.mock_client.get.return_value = {
            "accounts": ["U1234567"],
            "aliases": {"U1234567": "MyAccount"},
            "selectedAccount": "U1234567"
        }
        
        res = self.manager.list_accounts()
        self.assertEqual(len(res.accounts), 1)
        self.assertEqual(res.selectedAccount, "U1234567")
        self.mock_client.get.assert_called_with("/iserver/accounts")

    def test_get_pnl(self):
        """
        Test retrieving PnL data for the session.
        """
        # Mock Response for /iserver/account/pnl/partitioned
        self.mock_client.get.return_value = {
            "U1234567": {
                "rowType": 1,
                "pnl": 1000.5,
                "dpl": 10.0,
                "upl": 900.0,
                "rpl": 100.5
            }
        }
        
        res = self.manager.get_pnl()
        self.assertIn("U1234567", res.acctId)
        self.assertEqual(res.acctId["U1234567"].pnl, 1000.5)
        self.mock_client.get.assert_called_with("/iserver/account/pnl/partitioned")

    def test_get_signatures_and_owners(self):
        """
        Test retrieving signature and ownership information.
        """
        # Mock Response for /acesws/U1234567/signatures-and-owners
        self.mock_client.get.return_value = {
            "accountID": "U1234567",
            "entityType": "INDIVIDUAL",
            "applicants": [{"name": "John Doe", "role": "OWNER"}]
        }
        
        res = self.manager.get_signatures_and_owners("U1234567")
        self.assertEqual(res.accountID, "U1234567")
        self.assertEqual(res.entityType, "INDIVIDUAL")
        self.assertEqual(len(res.applicants), 1)
        self.mock_client.get.assert_called_with("/acesws/U1234567/signatures-and-owners")

if __name__ == "__main__":
    unittest.main()
