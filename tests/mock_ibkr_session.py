"""
Mock tests for IBKR Session tool.
This script tests the SessionManager logic by mocking the IBKRClient and the database.
"""
import unittest
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_session.core import SessionManager

class TestIBKRSession(unittest.TestCase):
    """
    Unit tests for SessionManager using mocked API and DB responses.
    """
    def setUp(self):
        self.mock_client_patcher = patch('tools.ibkr.ibkr_session.core.IBKRClient')
        self.mock_db_patcher = patch('tools.ibkr.ibkr_session.core.db_manager')
        
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_db_manager = self.mock_db_patcher.start()
        
        self.mock_client = self.mock_client_class.return_value
        self.manager = SessionManager()

    def tearDown(self):
        self.mock_client_patcher.stop()
        self.mock_db_patcher.stop()

    def test_get_status_authenticated(self):
        """Test checking status when authenticated."""
        self.mock_client.get.return_value = {
            "authenticated": True,
            "connected": True,
            "competing": False
        }
        res = self.manager.get_status()
        self.assertTrue(res.authenticated)
        self.mock_client.get.assert_called_with("/iserver/auth/status")

    def test_get_status_expired(self):
        """Test checking status when no longer authenticated (syncs DB)."""
        self.mock_client.get.return_value = {
            "authenticated": False,
            "connected": True,
            "competing": False
        }
        res = self.manager.get_status()
        self.assertFalse(res.authenticated)
        # Verify DB sync was attempted (check if execute was called to update status to EXPIRED)
        self.mock_db_manager.get_session.assert_called()

    def test_init_session(self):
        """Test initializing a new session."""
        self.mock_client.post.return_value = {"status": "ok"}
        res = self.manager.init_session()
        self.assertEqual(res["status"], "ok")
        self.mock_client.post.assert_called_with("/iserver/auth/ssodh/init")
        # Verify DB start was recorded
        self.mock_db_manager.get_session.assert_called()

    def test_logout(self):
        """Test logging out."""
        self.mock_client.post.return_value = {"confirmed": True}
        res = self.manager.logout()
        self.assertTrue(res["confirmed"])
        self.mock_client.post.assert_called_with("/logout")
        # Verify DB end was recorded
        self.mock_db_manager.get_session.assert_called()

    def test_tickle(self):
        """Test heartbeat (tickle)."""
        self.mock_client.post.return_value = {
            "session": "xyz",
            "ssoExpires": 1000,
            "collateral": True,
            "iserver": {}
        }
        res = self.manager.tickle()
        self.assertEqual(res.session, "xyz")
        self.mock_client.post.assert_called_with("/tickle")

    def test_reauthenticate(self):
        """Test re-authentication."""
        self.mock_client.post.return_value = {"message": "reauth initiated"}
        res = self.manager.reauthenticate()
        self.assertEqual(res["message"], "reauth initiated")
        self.mock_client.post.assert_called_with("/iserver/reauthenticate")

    # --- Error Cases ---

    def test_get_status_error(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_status()

    def test_init_session_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.init_session()

    def test_logout_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.logout()

    def test_tickle_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.tickle()

    def test_reauthenticate_error(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.reauthenticate()

    def test_db_failure_start(self):
        """Test graceful handling of DB failure during session start."""
        self.mock_client.post.return_value = {"status": "ok"}
        self.mock_db_manager.get_session.side_effect = Exception("DB Error")
        # Should not raise exception, just log error
        self.manager.init_session()
        self.mock_db_manager.get_session.assert_called()

    def test_db_failure_end(self):
        """Test graceful handling of DB failure during session end."""
        self.mock_client.post.return_value = {"status": "ok"}
        self.mock_db_manager.get_session.side_effect = Exception("DB Error")
        # Should not raise exception, just log error
        self.manager.logout()
        self.mock_db_manager.get_session.assert_called()

class TestIBKRSessionCLI(unittest.TestCase):
    """
    Unit tests for the CLI interface.
    """
    def setUp(self):
        self.manager_patcher = patch('tools.ibkr.ibkr_session.cli.SessionManager')
        self.mock_manager = self.manager_patcher.start()
        self.manager_instance = self.mock_manager.return_value
        
    def tearDown(self):
        self.manager_patcher.stop()

    def test_cli_status(self):
        from tools.ibkr.ibkr_session.cli import main
        # We need mock result to avoid model_dump truncation error in print
        self.manager_instance.get_status.return_value.model_dump_json.return_value = "{}"
        with patch('sys.argv', ['ibkr_session', 'status']):
            main()
            self.manager_instance.get_status.assert_called_once()

    def test_cli_init(self):
        from tools.ibkr.ibkr_session.cli import main
        self.manager_instance.init_session.return_value = {"status": "ok"}
        with patch('sys.argv', ['ibkr_session', 'init']):
            main()
            self.manager_instance.init_session.assert_called_once()

    def test_cli_logout(self):
        from tools.ibkr.ibkr_session.cli import main
        self.manager_instance.logout.return_value = {"confirmed": True}
        with patch('sys.argv', ['ibkr_session', 'logout']):
            main()
            self.manager_instance.logout.assert_called_once()

    def test_cli_tickle(self):
        from tools.ibkr.ibkr_session.cli import main
        mock_tickle = MagicMock()
        mock_tickle.model_dump_json.return_value = "{}"
        self.manager_instance.tickle.return_value = mock_tickle
        with patch('sys.argv', ['ibkr_session', 'tickle']):
            main()
            self.manager_instance.tickle.assert_called_once()

    def test_cli_reauth(self):
        from tools.ibkr.ibkr_session.cli import main
        self.manager_instance.reauthenticate.return_value = {"message": "ok"}
        with patch('sys.argv', ['ibkr_session', 'reauth']):
            main()
            self.manager_instance.reauthenticate.assert_called_once()

if __name__ == "__main__":
    unittest.main()
