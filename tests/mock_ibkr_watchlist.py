"""
Mock tests for IBKR Watchlist tool.
This script tests the WatchlistManager logic by mocking the IBKRClient.
"""
import unittest
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_watchlist.core import WatchlistManager

class TestIBKRWatchlist(unittest.TestCase):
    """
    Unit tests for WatchlistManager using mocked API responses.
    """
    def setUp(self):
        self.mock_client_patcher = patch('tools.ibkr.ibkr_watchlist.core.IBKRClient')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = self.mock_client_class.return_value
        self.manager = WatchlistManager()

    def tearDown(self):
        self.mock_client_patcher.stop()

    def test_list_watchlists(self):
        """Test listing all watchlists."""
        self.mock_client.get.return_value = {
            "USER": [{"id": "U1", "name": "MyList", "type": "USER"}],
            "SYST": [{"id": "S1", "name": "SystemList", "type": "SYST"}],
            "ALL": []
        }
        res = self.manager.list_watchlists()
        self.assertEqual(len(res.user_defined), 1)
        self.assertEqual(res.user_defined[0].name, "MyList")
        self.mock_client.get.assert_called_with("/iserver/watchlists")

    def test_get_watchlist(self):
        """Test getting specific watchlist detail."""
        self.mock_client.get.return_value = {
            "id": "U1",
            "name": "MyList",
            "rows": [{"conid": 265598, "symbol": "AAPL"}]
        }
        res = self.manager.get_watchlist("U1")
        self.assertEqual(res.name, "MyList")
        self.assertEqual(len(res.rows), 1)
        self.mock_client.get.assert_called_with("/iserver/watchlist", params={"id": "U1"})

    def test_create_watchlist(self):
        """Test creating a new watchlist."""
        self.mock_client.post.return_value = {"id": "U2", "name": "NewList"}
        res = self.manager.create_watchlist("NewList", [123, 456])
        self.assertEqual(res["name"], "NewList")
        self.mock_client.post.assert_called_once()
        args, kwargs = self.mock_client.post.call_args
        self.assertEqual(args[0], "/iserver/watchlist")
        self.assertEqual(kwargs['json_data']['name'], "NewList")
        self.assertEqual(len(kwargs['json_data']['rows']), 2)

    def test_delete_watchlist(self):
        """Test deleting a watchlist."""
        self.mock_client.delete.return_value = {"status": "ok"}
        res = self.manager.delete_watchlist("U1")
        self.assertEqual(res["status"], "ok")
        # The implementation uses a specific query param format in the tool logic
        self.mock_client.delete.assert_called_with("/iserver/watchlist?id=U1")

    def test_add_to_watchlist(self):
        """Test adding symbols (Fetch-Modify-Update)."""
        # 1. Mock the get call
        self.mock_client.get.return_value = {
            "id": "U1",
            "name": "MyList",
            "rows": [{"conid": 265598, "symbol": "AAPL"}]
        }
        # 2. Mock the post call
        self.mock_client.post.return_value = {"status": "ok"}
        
        res = self.manager.add_to_watchlist("U1", [789])
        
        self.assertEqual(res["status"], "ok")
        self.mock_client.get.assert_called_with("/iserver/watchlist", params={"id": "U1"})
        
        # Verify the post payload contains both old and new conids
        args, kwargs = self.mock_client.post.call_args
        rows = kwargs['json_data']['rows']
        conids = {r['conid'] for r in rows}
        self.assertIn(265598, conids)
        self.assertIn(789, conids)

    def test_remove_from_watchlist(self):
        """Test removing symbols (Fetch-Modify-Update)."""
        # 1. Mock the get call
        self.mock_client.get.return_value = {
            "id": "U1",
            "name": "MyList",
            "rows": [
                {"conid": 265598, "symbol": "AAPL"},
                {"conid": 789, "symbol": "MSFT"}
            ]
        }
        # 2. Mock the post call
        self.mock_client.post.return_value = {"status": "ok"}
        
        res = self.manager.remove_from_watchlist("U1", [265598])
        
        self.assertEqual(res["status"], "ok")
        # Verify the post payload contains only the remaining contract
        args, kwargs = self.mock_client.post.call_args
        rows = kwargs['json_data']['rows']
        rows = [r for r in rows if r.get('conid')]
        conids = {r['conid'] for r in rows}
        self.assertNotIn(265598, conids)
        self.assertIn(789, conids)

    # --- Error Cases ---
    def test_get_watchlist_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_watchlist("U1")

    def test_create_watchlist_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.create_watchlist("List", [123])

class TestIBKRWatchlistCLI(unittest.TestCase):
    """
    Unit tests for the CLI interface.
    """
    def setUp(self):
        self.manager_patcher = patch('tools.ibkr.ibkr_watchlist.cli.WatchlistManager')
        self.mock_manager = self.manager_patcher.start()
        self.manager_instance = self.mock_manager.return_value
        
    def tearDown(self):
        self.manager_patcher.stop()

    def test_cli_list(self):
        from tools.ibkr.ibkr_watchlist.cli import main
        mock_res = MagicMock()
        mock_res.model_dump_json.return_value = "{}"
        self.manager_instance.list_watchlists.return_value = mock_res
        
        with patch('sys.argv', ['ibkr_watchlist', 'list']):
            main()
            self.manager_instance.list_watchlists.assert_called_once()

    def test_cli_get(self):
        from tools.ibkr.ibkr_watchlist.cli import main
        mock_res = MagicMock()
        mock_res.model_dump_json.return_value = "{}"
        self.manager_instance.get_watchlist.return_value = mock_res
        with patch('sys.argv', ['ibkr_watchlist', 'get', '--id', 'U1']):
            main()
            self.manager_instance.get_watchlist.assert_called_with('U1')

    def test_cli_create(self):
        from tools.ibkr.ibkr_watchlist.cli import main
        self.manager_instance.create_watchlist.return_value = {"id": "U2"}
        with patch('sys.argv', ['ibkr_watchlist', 'create', '--name', 'MyWL', '--conids', '123', '456']):
            main()
            self.manager_instance.create_watchlist.assert_called_once_with('MyWL', [123, 456])

    def test_cli_delete(self):
        from tools.ibkr.ibkr_watchlist.cli import main
        self.manager_instance.delete_watchlist.return_value = {"status": "ok"}
        with patch('sys.argv', ['ibkr_watchlist', 'delete', '--id', 'U1']):
            main()
            self.manager_instance.delete_watchlist.assert_called_with('U1')

    def test_cli_add(self):
        from tools.ibkr.ibkr_watchlist.cli import main
        self.manager_instance.add_to_watchlist.return_value = {"status": "ok"}
        with patch('sys.argv', ['ibkr_watchlist', 'add', '--id', 'U1', '--conids', '789']):
            main()
            self.manager_instance.add_to_watchlist.assert_called_with('U1', [789])

    def test_cli_remove(self):
        from tools.ibkr.ibkr_watchlist.cli import main
        self.manager_instance.remove_from_watchlist.return_value = {"status": "ok"}
        with patch('sys.argv', ['ibkr_watchlist', 'remove', '--id', 'U1', '--conids', '123']):
            main()
            self.manager_instance.remove_from_watchlist.assert_called_with('U1', [123])

if __name__ == "__main__":
    unittest.main()
