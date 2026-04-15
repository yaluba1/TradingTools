"""
Mock tests for IBKR Orders tool.
This script tests the OrdersManager logic by mocking the IBKRClient and database session.
"""
import unittest
import json
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_orders.core import OrdersManager
from tools.ibkr.schemas.order_schemas import OrderRequest

class TestIBKROrders(unittest.TestCase):
    def setUp(self):
        # Patch IBKRClient and DatabaseManager to avoid real network/DB calls
        self.mock_client_patcher = patch('tools.ibkr.ibkr_orders.core.IBKRClient')
        self.mock_db_patcher = patch('tools.ibkr.ibkr_orders.core.db_manager')
        
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_db_manager = self.mock_db_patcher.start()
        
        self.mock_client = self.mock_client_class.return_value
        # Mock the logger inside the client
        self.mock_client.logger = MagicMock()
        
        # Mock the database session context manager
        self.mock_session = MagicMock()
        self.mock_db_manager.get_session.return_value.__enter__.return_value = self.mock_session
        
        self.manager = OrdersManager()

    def tearDown(self):
        self.mock_client_patcher.stop()
        self.mock_db_patcher.stop()

    def test_place_order_direct_success(self):
        # Mock successful placement response
        self.mock_client.post.return_value = [
            {
                "order_id": "1001",
                "order_status": "PreSubmitted",
                "local_order_id": "cust-123"
            }
        ]
        
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=10,
            price=150.0,
            cId="cust-123"
        )
        
        results = self.manager.place_order("U123", request)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].order_id, "1001")
        # Verify DB calls for saving order and logging event
        self.assertTrue(self.mock_session.execute.called)
        # Verify API call
        self.mock_client.post.assert_called_with("/iserver/account/U123/orders", json_data={"orders": [request.model_dump()]})

    def test_place_order_with_auto_confirm(self):
        # Mock initial question response
        self.mock_client.post.side_effect = [
            # First call returns a question
            [{"id": "q-1", "message": ["Price is too far from market"]}],
            # Second call (the reply) returns success
            [{"order_id": "1002", "order_status": "Submitted"}]
        ]
        
        request = OrderRequest(
            conid=265598,
            orderType="MKT",
            side="BUY",
            quantity=5,
            cId="cust-456"
        )
        
        results = self.manager.place_order("U123", request, auto_confirm=True)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].order_id, "1002")
        # Verify reply was sent automatically
        self.mock_client.post.assert_any_call("/iserver/reply/q-1", json_data={"confirmed": True})

    def test_sync_orders(self):
        # Mock live orders response
        self.mock_client.get.return_value = {
            "U123": [
                {
                    "orderId": "1001",
                    "conid": 265598,
                    "side": "BUY",
                    "orderType": "LMT",
                    "totalSize": 10.0,
                    "cumFill": 5.0,
                    "avgPrice": 149.0,
                    "status": "PartiallyFilled",
                    "timeInForce": "DAY",
                    "account": "U123"
                }
            ]
        }
        
        # Mock DB select to find the order
        self.mock_session.execute.return_value.fetchone.return_value = ("cust-123", "PendingSubmit", 0.0)
        
        results = self.manager.sync_orders("U123")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].new_status, "PartiallyFilled")
        self.assertEqual(results[0].filled_increment, 5.0)
        # Verify DB update call
        self.assertTrue(self.mock_session.execute.called)

    def test_get_questions(self):
        # Mock questions response
        self.mock_client.get.return_value = [
            {"id": "q-1", "text": ["Confirm short position"]}
        ]
        
        questions = self.manager.get_questions()
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].id, "q-1")
        self.assertEqual(questions[0].text[0], "Confirm short position")

    def test_list_live_orders_filter(self):
        # Mock live orders response
        self.mock_client.get.return_value = {
            "U123": [
                {
                    "orderId": "1001",
                    "conid": 265598,
                    "side": "BUY",
                    "orderType": "LMT",
                    "totalSize": 10.0,
                    "cumFill": 0.0,
                    "avgPrice": 0.0,
                    "status": "Submitted",
                    "timeInForce": "DAY",
                    "account": "U123"
                },
                {
                    "orderId": "1002",
                    "conid": 265599,
                    "side": "SELL",
                    "orderType": "MKT",
                    "totalSize": 5.0,
                    "cumFill": 5.0,
                    "avgPrice": 50.0,
                    "status": "Filled",
                    "timeInForce": "DAY",
                    "account": "U123"
                }
            ]
        }
        
        # Test unfiltered
        orders = self.manager.list_live_orders("U123")
        self.assertEqual(len(orders), 2)
        
        # Test filtered by Filled
        filled_orders = self.manager.list_live_orders("U123", status_filter="Filled")
        self.assertEqual(len(filled_orders), 1)
        self.assertEqual(filled_orders[0].orderId, "1002")

if __name__ == "__main__":
    unittest.main()
