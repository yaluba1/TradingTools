"""
Mock tests for IBKR Portfolio tool.
This script tests the PortfolioManager logic by mocking the IBKRClient.
"""
import unittest
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_portfolio.core import PortfolioManager

class TestIBKRPortfolio(unittest.TestCase):
    """
    Unit tests for PortfolioManager using mocked API responses.
    """
    def setUp(self):
        """
        Initialize the test case by patching dependencies.
        """
        self.mock_client_patcher = patch('tools.ibkr.ibkr_portfolio.core.IBKRClient')
        self.mock_db_patcher = patch('tools.ibkr.common.logger.db_manager')
        
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_db_manager = self.mock_db_patcher.start()
        
        self.mock_client = self.mock_client_class.return_value
        self.manager = PortfolioManager()

    def tearDown(self):
        """
        Clean up patchers after each test.
        """
        self.mock_client_patcher.stop()
        self.mock_db_patcher.stop()

    def test_list_accounts(self):
        """Test retrieving portfolio accounts."""
        self.mock_client.get.return_value = [
            {"id": "U1234567", "accountId": "U1234567", "displayName": "Main"}
        ]
        res = self.manager.list_accounts()
        self.assertEqual(len(res.accounts), 1)
        self.assertEqual(res.accounts[0].accountId, "U1234567")
        self.mock_client.get.assert_called_with("/portfolio/accounts")

    def test_get_summary(self):
        """Test retrieving portfolio summary."""
        self.mock_client.get.return_value = {
            "accountsummaries": [
                {"account": "U1234567", "key": "NetLiquidation", "value": "10000.0"}
            ]
        }
        res = self.manager.get_summary("U1234567")
        self.assertEqual(len(res.summary), 1)
        self.assertEqual(res.summary[0].key, "NetLiquidation")
        self.mock_client.get.assert_called_with("/portfolio/U1234567/summary")

    def test_get_ledger(self):
        """Test retrieving portfolio ledger."""
        self.mock_client.get.return_value = {
            "USD": {"ca": 5000.0, "se": 2000.0, "ni": 7000.0}
        }
        res = self.manager.get_ledger("U1234567")
        self.assertIn("USD", res.ledger)
        self.assertEqual(res.ledger["USD"].cashbalance, 5000.0)
        self.mock_client.get.assert_called_with("/portfolio/U1234567/ledger")

    def test_get_positions(self):
        """Test retrieving portfolio positions."""
        self.mock_client.get.return_value = [
            {"acctId": "U1234567", "conid": 265598, "position": 100, "mktPrice": 150.0, 
             "mktValue": 15000.0, "currency": "USD", "avgCost": 140.0}
        ]
        res = self.manager.get_positions("U1234567", 0)
        self.assertEqual(len(res.positions), 1)
        self.assertEqual(res.positions[0].symbol, None) # IBKR symbol is optional in this endpoint
        self.assertEqual(res.positions[0].conid, 265598)
        self.mock_client.get.assert_called_with("/portfolio/U1234567/positions/0")

    def test_invalidate_positions(self):
        """Test invalidating positions cache."""
        self.mock_client.post.return_value = {"status": "ok"}
        res = self.manager.invalidate_positions()
        self.assertEqual(res["status"], "ok")
        self.mock_client.post.assert_called_with("/portfolio/positions/invalidate")

    def test_get_allocation(self):
        """Test retrieving allocation data."""
        self.mock_client.get.return_value = {
            "assetClass": [{"group": "Stocks", "val": 10000.0, "pct": 100.0}],
            "sector": [],
            "grouping": []
        }
        res = self.manager.get_allocation("U1234567")
        self.assertEqual(len(res.assetClass), 1)
        self.assertEqual(res.assetClass[0].group, "Stocks")
        self.mock_client.get.assert_called_with("/portfolio/U1234567/allocation")

    def test_get_performance(self):
        """Test retrieving PA performance data."""
        self.mock_client.post.return_value = {
            "id": "perf1",
            "nav": {"data": [{"v": 10000.0, "p": "2023-01-01"}]}
        }
        res = self.manager.get_performance(["U1234567"], "D")
        self.assertEqual(res.id, "perf1")
        self.assertIsNotNone(res.nav)
        self.assertEqual(res.nav.data[0].val, 10000.0)
        self.mock_client.post.assert_called()

    def test_get_pa_summary(self):
        """Test retrieving PA summary data."""
        self.mock_client.post.return_value = {"whatever": "data"}
        res = self.manager.get_pa_summary(["U1234567"])
        self.mock_client.post.assert_called_with("/pa/summary", json_data={"acctIds": ["U1234567"]})

    def test_get_transactions(self):
        """Test retrieving PA transactions data."""
        self.mock_client.post.return_value = [
            {"acctid": "U1234567", "conid": 265598, "symbol": "AAPL", "side": "BUY", 
             "qty": 10, "pr": 150.0, "amt": 1500.0, "comm": 1.0, "date": "2023-01-01", "type": "TRADE"}
        ]
        res = self.manager.get_transactions(["U1234567"], days=30)
        self.assertEqual(len(res.transactions), 1)
        self.assertEqual(res.transactions[0].symbol, "AAPL")
        self.mock_client.post.assert_called_with("/pa/transactions", json_data={"acctIds": ["U1234567"], "days": 30})

    # --- Error Cases ---

    def test_list_accounts_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.list_accounts()

    def test_get_summary_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_summary("U1234567")

    def test_get_ledger_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_ledger("U1234567")

    def test_get_positions_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_positions("U1234567")

    def test_invalidate_positions_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.invalidate_positions()

    def test_get_allocation_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_allocation()

    def test_get_performance_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_performance(["U1234567"])

    def test_get_pa_summary_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_pa_summary(["U1234567"])

    def test_get_transactions_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_transactions(["U1234567"])

class TestIBKRPortfolioCLI(unittest.TestCase):
    """
    Unit tests for the CLI interface.
    """
    def setUp(self):
        self.manager_patcher = patch('tools.ibkr.ibkr_portfolio.cli.PortfolioManager')
        self.mock_manager = self.manager_patcher.start()
        self.manager_instance = self.mock_manager.return_value
        
    def tearDown(self):
        self.manager_patcher.stop()

    def test_cli_accounts(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'accounts']):
            main()
            self.manager_instance.list_accounts.assert_called_once()

    def test_cli_summary(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'summary', '--account', 'U1234567']):
            main()
            self.manager_instance.get_summary.assert_called_with('U1234567')

    def test_cli_ledger(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'ledger', '--account', 'U1234567']):
            main()
            self.manager_instance.get_ledger.assert_called_with('U1234567')

    def test_cli_positions(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'positions', '--account', 'U1234567', '--page', '1']):
            main()
            self.manager_instance.get_positions.assert_called_with('U1234567', 1)

    def test_cli_invalidate(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        self.manager_instance.invalidate_positions.return_value = {"status": "ok"}
        with patch('sys.argv', ['ibkr_portfolio', 'invalidate']):
            main()
            self.manager_instance.invalidate_positions.assert_called_once()

    def test_cli_allocation(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'allocation', '--account', 'U1234567']):
            main()
            self.manager_instance.get_allocation.assert_called_with('U1234567')

    def test_cli_performance(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'performance', '--accounts', 'U1,U2', '--freq', 'M']):
            # argparse splits by space usually, but here it's nargs='+'
            # The test should pass the accounts as separate args or check how argparse handles it
            pass 
        
        with patch('sys.argv', ['ibkr_portfolio', 'performance', '--accounts', 'U1', 'U2', '--freq', 'M']):
            main()
            self.manager_instance.get_performance.assert_called_with(['U1', 'U2'], 'M')

    def test_cli_pa_summary(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'pa-summary', '--accounts', 'U1']):
            main()
            self.manager_instance.get_pa_summary.assert_called_with(['U1'])

    def test_cli_transactions(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'transactions', '--accounts', 'U1', '--conid', '123', '--days', '7']):
            main()
            self.manager_instance.get_transactions.assert_called_with(['U1'], 123, 7)

if __name__ == "__main__":
    unittest.main()
