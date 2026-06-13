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
            "netliquidation": {
                "amount": 10000.0,
                "currency": "USD",
                "isNull": False,
                "timestamp": 1781292741000,
                "value": None,
                "severity": 0
            }
        }
        res = self.manager.get_summary("U1234567")
        self.assertIn("netliquidation", res.summary)
        self.assertEqual(res.summary["netliquidation"].amount, 10000.0)
        self.assertEqual(res.summary["netliquidation"].currency, "USD")
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

    def test_get_positions_nocache(self):
        """Test retrieving near-real-time (uncached) positions."""
        self.mock_client.get.return_value = [
            {"acctId": "U1234567", "conid": 265598, "position": 100, "mktPrice": 150.0, 
             "mktValue": 15000.0, "currency": "USD", "avgCost": 140.0}
        ]
        # Test default call (no query params)
        res = self.manager.get_positions_nocache("U1234567")
        self.assertEqual(len(res.positions), 1)
        self.assertEqual(res.positions[0].conid, 265598)
        self.mock_client.get.assert_called_with("/portfolio2/U1234567/positions", params={})

        # Test with query parameters
        res = self.manager.get_positions_nocache("U1234567", model="modelA", sort="position", direction="d")
        self.assertEqual(len(res.positions), 1)
        self.mock_client.get.assert_called_with(
            "/portfolio2/U1234567/positions",
            params={"model": "modelA", "sort": "position", "direction": "d"}
        )

    def test_invalidate_positions(self):
        """Test invalidating positions cache."""
        self.mock_client.post.return_value = {"status": "ok"}
        res = self.manager.invalidate_positions("U1234567")
        self.assertEqual(res["status"], "ok")
        self.mock_client.post.assert_called_with("/portfolio/U1234567/positions/invalidate")

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

    def test_get_allocation_new_format(self):
        """Test retrieving allocation data in the new nested dictionary format."""
        self.mock_client.get.return_value = {
            "assetClass": {
                "long": {"STK": 41252.15, "CASH": 262.64},
                "short": {}
            },
            "sector": {
                "long": {"Energy": 1260.02, "Technology": 25170.84},
                "short": {}
            },
            "group": {
                "long": {"Computers": 20382.80},
                "short": {}
            }
        }
        res = self.manager.get_allocation("U1234567")
        self.assertIsNotNone(res.assetClass)
        self.assertEqual(res.assetClass.long["STK"], 41252.15)
        self.assertEqual(res.assetClass.long["CASH"], 262.64)
        self.assertEqual(res.sector.long["Technology"], 25170.84)
        self.assertEqual(res.group.long["Computers"], 20382.80)
        self.assertIsNone(res.grouping)
        self.mock_client.get.assert_called_with("/portfolio/U1234567/allocation")

    def test_get_performance(self):
        """Test retrieving PA performance data."""
        self.mock_client.post.return_value = {
            "id": "perf1",
            "nav": {"data": [{"v": 10000.0, "p": "2023-01-01"}]}
        }
        res = self.manager.get_performance(["U1234567"], "12M")
        self.assertEqual(res.id, "perf1")
        self.assertIsNotNone(res.nav)
        self.assertEqual(res.nav.data[0].val, 10000.0)
        self.mock_client.post.assert_called_with("/pa/performance", json_data={"acctIds": ["U1234567"], "period": "1Y"})

    def test_get_performance_all_periods(self):
        """Test retrieving PA performance data for all periods."""
        self.mock_client.post.return_value = {
            "id": "perf_all",
            "nav": {"data": [{"v": 12000.0, "p": "2023-01-01"}]}
        }
        res = self.manager.get_performance_all_periods(["U1234567"])
        self.assertEqual(res.id, "perf_all")
        self.assertIsNotNone(res.nav)
        self.assertEqual(res.nav.data[0].val, 12000.0)
        self.mock_client.post.assert_called_with("/pa/allperiods", json_data={"acctIds": ["U1234567"]})

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
        res = self.manager.get_transactions(["U1234567"], [265598], "USD", days=30)
        self.assertEqual(len(res.transactions), 1)
        self.assertEqual(res.transactions[0].symbol, "AAPL")
        self.mock_client.post.assert_called_with("/pa/transactions", json_data={
            "acctIds": ["U1234567"],
            "conids": [265598],
            "currency": "USD",
            "days": 30
        })

    def test_list_subaccounts(self):
        """Test retrieving portfolio sub-accounts."""
        self.mock_client.get.return_value = [
            {"id": "U7654321", "accountId": "U7654321", "displayName": "Sub-Account"}
        ]
        res = self.manager.list_subaccounts()
        self.assertEqual(len(res.subaccounts), 1)
        self.assertEqual(res.subaccounts[0].accountId, "U7654321")
        self.mock_client.get.assert_called_with("/portfolio/subaccounts")

    def test_get_positions_by_conid(self):
        """Test retrieving all account positions in an instrument conid."""
        self.mock_client.get.return_value = {
            "U1234567": [
                {"acctId": "U1234567", "conid": 265598, "position": 100, "mktPrice": 150.0, 
                 "mktValue": 15000.0, "currency": "USD", "avgCost": 140.0}
            ]
        }
        res = self.manager.get_positions_by_conid(265598)
        self.assertIn("U1234567", res.root)
        self.assertEqual(len(res.root["U1234567"]), 1)
        self.assertEqual(res.root["U1234567"][0].conid, 265598)
        self.mock_client.get.assert_called_with("/portfolio/positions/265598")

    def test_get_account_meta(self):
        """Test retrieving portfolio account metadata."""
        self.mock_client.get.return_value = {
            "id": "U1234567",
            "accountId": "U1234567",
            "displayName": "Main Account",
            "currency": "USD"
        }
        res = self.manager.get_account_meta("U1234567")
        self.assertEqual(res.accountId, "U1234567")
        self.assertEqual(res.baseCurrency, "USD")
        self.mock_client.get.assert_called_with("/portfolio/U1234567/meta")

    def test_get_position_by_conid(self):
        """Test retrieving position detail by conid."""
        self.mock_client.get.return_value = [
            {"acctId": "U1234567", "conid": 265598, "position": 100, "mktPrice": 150.0, 
             "mktValue": 15000.0, "currency": "USD", "avgCost": 140.0}
        ]
        res = self.manager.get_position_by_conid("U1234567", 265598)
        self.assertEqual(len(res.positions), 1)
        self.assertEqual(res.positions[0].conid, 265598)
        self.mock_client.get.assert_called_with("/portfolio/U1234567/position/265598")

    def test_get_pa_allocation(self):
        """Test retrieving PA allocation data."""
        self.mock_client.post.return_value = {
            "id": "getAllocation",
            "currency": "USD",
            "realtime": False,
            "date": "20260612",
            "allocations": {
                "ASSET_CLASS": {
                    "long": {
                        "total": {"nav": 15000.0, "weight": 1.0},
                        "items": [
                            {"id": "EQ", "name": "Equities", "nav": 15000.0, "weight": 1.0, "color": "#d780ff"}
                        ]
                    }
                }
            }
        }
        # Test with mandatory + optional arguments
        res = self.manager.get_pa_allocation(["U1234567"], type="ALL", currency="USD", date="20260613", model="model1")
        self.assertEqual(res.id, "getAllocation")
        self.assertIn("ASSET_CLASS", res.allocations)
        self.assertEqual(res.allocations["ASSET_CLASS"].long.total.nav, 15000.0)
        self.assertEqual(res.allocations["ASSET_CLASS"].long.items[0].name, "Equities")
        self.mock_client.post.assert_called_with(
            "/pa/allocation",
            json_data={
                "acctIds": ["U1234567"],
                "type": "ALL",
                "currency": "USD",
                "date": "20260613",
                "model": "model1"
            }
        )

        # Test with only mandatory arguments
        res_mandatory = self.manager.get_pa_allocation(["U1234567"], type="ASSET_CLASS")
        self.assertEqual(res_mandatory.id, "getAllocation")
        self.mock_client.post.assert_called_with(
            "/pa/allocation",
            json_data={
                "acctIds": ["U1234567"],
                "type": "ASSET_CLASS"
            }
        )

    def test_get_positions_no_page(self):
        """Test retrieving portfolio positions without specifying page ID."""
        self.mock_client.get.return_value = []
        res = self.manager.get_positions("U1234567")
        self.assertEqual(len(res.positions), 0)
        self.mock_client.get.assert_called_with("/portfolio/U1234567/positions")

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
            self.manager.invalidate_positions("U1234567")

    def test_get_allocation_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_allocation()

    def test_get_performance_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_performance(["U1234567"])

    def test_get_performance_all_periods_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_performance_all_periods(["U1234567"])

    def test_get_pa_summary_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_pa_summary(["U1234567"])

    def test_get_transactions_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_transactions(["U1234567"], [265598], "USD")

    def test_list_subaccounts_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.list_subaccounts()

    def test_get_positions_by_conid_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_positions_by_conid(265598)

    def test_get_account_meta_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_account_meta("U1234567")

    def test_get_position_by_conid_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_position_by_conid("U1234567", 265598)

    def test_get_pa_allocation_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_pa_allocation(["U1234567"], type="ALL")

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
        with patch('sys.argv', ['ibkr_portfolio', 'invalidate', '--account', 'U1234567']):
            main()
            self.manager_instance.invalidate_positions.assert_called_with('U1234567')

    def test_cli_allocation(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'allocation', '--account', 'U1234567']):
            main()
            self.manager_instance.get_allocation.assert_called_with('U1234567')

    def test_cli_performance(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'performance', '--accounts', 'U1', 'U2', '--period', '1M']):
            main()
            self.manager_instance.get_performance.assert_called_with(['U1', 'U2'], '1M')
            
        with patch('sys.argv', ['ibkr_portfolio', 'performance', '--accounts', 'U1', 'U2']):
            main()
            self.manager_instance.get_performance.assert_called_with(['U1', 'U2'], '12M')

    def test_cli_performance_all(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'performance-all', '--accounts', 'U1', 'U2']):
            main()
            self.manager_instance.get_performance_all_periods.assert_called_with(['U1', 'U2'])

    def test_cli_pa_summary(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'pa-summary', '--accounts', 'U1']):
            main()
            self.manager_instance.get_pa_summary.assert_called_with(['U1'])

    def test_cli_transactions(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        # Test CLI call with specific days
        with patch('sys.argv', ['ibkr_portfolio', 'transactions', '--accounts', 'U1', '--conids', '123', '456', '--currency', 'USD', '--days', '7']):
            main()
            self.manager_instance.get_transactions.assert_called_with(
                account_ids=['U1'],
                conids=[123, 456],
                currency='USD',
                days=7
            )
            
        # Test CLI call with default days (90)
        with patch('sys.argv', ['ibkr_portfolio', 'transactions', '--accounts', 'U1', '--conids', '123', '--currency', 'USD']):
            main()
            self.manager_instance.get_transactions.assert_called_with(
                account_ids=['U1'],
                conids=[123],
                currency='USD',
                days=90
            )

    def test_cli_subaccounts(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'subaccounts']):
            main()
            self.manager_instance.list_subaccounts.assert_called_once()

    def test_cli_positions_conid(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'positions-conid', '--conid', '265598']):
            main()
            self.manager_instance.get_positions_by_conid.assert_called_with(265598)

    def test_cli_meta(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'meta', '--account', 'U1234567']):
            main()
            self.manager_instance.get_account_meta.assert_called_with('U1234567')

    def test_cli_position(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        with patch('sys.argv', ['ibkr_portfolio', 'position', '--account', 'U1234567', '--conid', '265598']):
            main()
            self.manager_instance.get_position_by_conid.assert_called_with('U1234567', 265598)

    def test_cli_pa_allocation(self):
        from tools.ibkr.ibkr_portfolio.cli import main
        # Test with mandatory + optional arguments
        with patch('sys.argv', [
            'ibkr_portfolio', 'pa-allocation',
            '--accounts', 'U1234567',
            '--type', 'ALL',
            '--currency', 'USD',
            '--date', '20260613',
            '--model', 'model1'
        ]):
            main()
            self.manager_instance.get_pa_allocation.assert_called_with(
                account_ids=['U1234567'],
                type='ALL',
                currency='USD',
                date='20260613',
                model='model1'
            )

        # Test with only mandatory arguments
        with patch('sys.argv', [
            'ibkr_portfolio', 'pa-allocation',
            '--accounts', 'U1234567',
            '--type', 'ASSET_CLASS'
        ]):
            main()
            self.manager_instance.get_pa_allocation.assert_called_with(
                account_ids=['U1234567'],
                type='ASSET_CLASS',
                currency=None,
                date=None,
                model=None
            )

if __name__ == "__main__":
    unittest.main()
