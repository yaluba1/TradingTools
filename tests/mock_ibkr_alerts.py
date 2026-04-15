"""
Mock tests for IBKR Alerts tool.
This script tests the AlertsManager logic by mocking the IBKRClient.
"""
import unittest
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_alerts.core import AlertsManager
from tools.ibkr.schemas.alert_schemas import AlertCreateRequest, AlertCondition

class TestIBKRAlerts(unittest.TestCase):
    def setUp(self):
        # Patch IBKRClient and DatabaseManager to avoid real network/DB calls
        self.mock_client_patcher = patch('tools.ibkr.ibkr_alerts.core.IBKRClient')
        self.mock_db_patcher = patch('tools.ibkr.common.logger.db_manager')
        
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_db_manager = self.mock_db_patcher.start()
        
        self.mock_client = self.mock_client_class.return_value
        self.manager = AlertsManager()

    def tearDown(self):
        self.mock_client_patcher.stop()
        self.mock_db_patcher.stop()

    def test_list_alerts(self):
        # Mock list response
        self.mock_client.get.return_value = [
            {
                "order_id": 123,
                "account": "U123",
                "alert_name": "Test Alert",
                "alert_active": 1,
                "order_time": "20230101-12:00:00",
                "alert_triggered": False,
                "alert_repeatable": 0
            }
        ]
        
        alerts = self.manager.list_alerts("U123")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].alert_name, "Test Alert")
        self.mock_client.get.assert_called_with("/iserver/account/U123/alerts")

    def test_create_alert_new(self):
        # Mock empty list (no existing alert with same name)
        self.mock_client.get.return_value = []
        # Mock create response
        self.mock_client.post.return_value = {
            "order_id": 456,
            "success": True,
            "text": "Submitted"
        }
        
        request = AlertCreateRequest(
            alertName="New Alert",
            alertMessage="Msg",
            conditions=[AlertCondition(type=1, operator=">=", value="100", conidex="123@SMART")]
        )
        
        response = self.manager.create_or_modify_alert("U123", request)
        self.assertTrue(response.success)
        self.assertEqual(response.order_id, 456)
        # Verify POST was called for creation (no alertId in payload)
        call_args = self.mock_client.post.call_args[1]["json_data"]
        self.assertNotIn("alertId", call_args)

    def test_create_alert_modify_existing(self):
        # Mock list containing an alert with the same name
        self.mock_client.get.return_value = [
            {
                "order_id": 123,
                "account": "U123",
                "alert_name": "Existing Alert",
                "alert_active": 1,
                "order_time": "20230101-12:00:00",
                "alert_triggered": False,
                "alert_repeatable": 0
            }
        ]
        # Mock modify response
        self.mock_client.post.return_value = {
            "order_id": 123,
            "success": True,
            "text": "Modified"
        }
        
        request = AlertCreateRequest(
            alertName="Existing Alert",
            alertMessage="Updated Msg",
            conditions=[AlertCondition(type=1, operator=">=", value="110", conidex="123@SMART")]
        )
        
        response = self.manager.create_or_modify_alert("U123", request)
        self.assertTrue(response.success)
        # Verify POST was called with alertId for modification
        call_args = self.mock_client.post.call_args[1]["json_data"]
        self.assertEqual(call_args["alertId"], 123)

if __name__ == "__main__":
    unittest.main()
