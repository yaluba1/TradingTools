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

    def test_modify_order_success(self):
        # Mock successful modification response
        self.mock_client.post.return_value = [
            {
                "order_id": "1001",
                "order_status": "Submitted",
                "local_order_id": "cust-123"
            }
        ]
        
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=15,
            price=149.0,
            cId="cust-123"
        )
        
        results = self.manager.modify_order("U123", "1001", request)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].order_id, "1001")
        self.assertEqual(request.acctId, "U123")
        # Verify DB updates were called for saving/logging modified order
        self.assertTrue(self.mock_session.execute.called)
        # Verify API call to singular modify order endpoint
        self.mock_client.post.assert_called_with("/iserver/account/U123/order/1001", json_data=request.model_dump())

    def test_modify_order_with_auto_confirm(self):
        # Mock initial question response and then the reply response
        self.mock_client.post.side_effect = [
            # First call returns a warning
            [{"id": "q-modify-1", "message": ["Price deviates from last price"]}],
            # Second call (the reply) returns success
            [{"order_id": "1001", "order_status": "Submitted", "local_order_id": "cust-123"}]
        ]
        
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=15,
            price=149.0,
            cId="cust-123"
        )
        
        # Mock DB select to find the existing customer order ID (so the DB flow works)
        self.mock_session.execute.return_value.fetchone.return_value = ("cust-123",)
        
        results = self.manager.modify_order("U123", "1001", request, auto_confirm=True)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].order_id, "1001")
        # Verify reply was sent automatically
        self.mock_client.post.assert_any_call("/iserver/reply/q-modify-1", json_data={"confirmed": True})

    def test_preview_orders_success(self):
        # Mock whatif response
        self.mock_client.post.return_value = {
            "amount": {
                "amount": "1,500 USD (100 Shares)",
                "commission": "1.00 USD",
                "total": "1,501.00 USD"
            },
            "equity": {
                "current": "95,000",
                "change": "0",
                "after": "95,000"
            },
            "initial": {
                "current": "5,000",
                "change": "500",
                "after": "5,500"
            },
            "maintenance": {
                "current": "4,000",
                "change": "400",
                "after": "4,400"
            },
            "position": {
                "current": "0",
                "change": "100",
                "after": "100"
            },
            "warn": "warning message",
            "error": None,
            "warns": ["warning message"],
            "accruedInterest": None
        }
        
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=10,
            price=150.0,
            cId="cust-123"
        )
        
        result = self.manager.preview_orders("U123", request)
        
        self.assertEqual(result.amount.amount, "1,500 USD (100 Shares)")
        self.assertEqual(result.equity.current, "95,000")
        self.assertEqual(result.amount.commission, "1.00 USD")
        self.assertEqual(result.warn, "warning message")
        self.mock_client.post.assert_called_with("/iserver/account/U123/orders/whatif", json_data={"orders": [request.model_dump()]})

    def test_suppress_questions_success(self):
        # Mock suppress response
        self.mock_client.post.return_value = {"status": "suppressed"}
        
        result = self.manager.suppress_questions(["o163", "o10082"])
        
        self.assertEqual(result.get("status"), "suppressed")
        self.mock_client.post.assert_called_with("/iserver/questions/suppress", json_data={"messageIds": ["o163", "o10082"]})

    def test_reset_suppression_success(self):
        # Mock reset response
        self.mock_client.post.return_value = {"status": "reset"}
        
        result = self.manager.reset_suppression()
        
        self.assertEqual(result.get("status"), "reset")
        self.mock_client.post.assert_called_with("/iserver/questions/suppress/reset")

    def test_list_live_orders_with_params(self):
        # Mock response
        self.mock_client.get.return_value = {"U123": []}
        
        orders = self.manager.list_live_orders(account_id="U123", filters="active", force=True)
        
        self.assertEqual(len(orders), 0)
        self.mock_client.get.assert_called_with("/iserver/account/orders", params={"accountId": "U123", "filters": "active", "force": "true"})

    def test_list_live_orders_normalization_submitted(self):
        self.mock_client.get.return_value = {"U123": []}
        orders = self.manager.list_live_orders(account_id="U123", filters="submitted")
        self.assertEqual(len(orders), 0)
        self.mock_client.get.assert_called_with("/iserver/account/orders", params={"accountId": "U123", "filters": "Submitted"})

    def test_list_live_orders_normalization_comma_separated(self):
        self.mock_client.get.return_value = {"U123": []}
        orders = self.manager.list_live_orders(account_id="U123", filters="submitted,filled")
        self.assertEqual(len(orders), 0)
        self.mock_client.get.assert_called_with("/iserver/account/orders", params={"accountId": "U123", "filters": "Submitted,Filled"})

    def test_list_live_orders_auto_filters_from_status(self):
        self.mock_client.get.return_value = {"U123": []}
        orders = self.manager.list_live_orders(account_id="U123", status_filter="Submitted")
        self.assertEqual(len(orders), 0)
        self.mock_client.get.assert_called_with("/iserver/account/orders", params={"accountId": "U123", "filters": "Submitted"})

    def test_list_live_orders_extra_fields(self):
        self.mock_client.get.return_value = {
            "orders": [
                {
                    "acct": "DU7126953",
                    "conidex": "468091282",
                    "conid": 468091282,
                    "account": "DU7126953",
                    "orderId": 761319201,
                    "cashCcy": "USD",
                    "sizeAndFills": "0/1,000",
                    "orderDesc": "Buy 1000 ZIM Limit 15.51, Day",
                    "description1": "ZIM",
                    "ticker": "ZIM",
                    "secType": "STK",
                    "listingExchange": "NYSE",
                    "remainingQuantity": 1000.0,
                    "filledQuantity": 0.0,
                    "totalSize": 1000.0,
                    "companyName": "ZIM INTEGRATED SHIPPING SERV",
                    "status": "Submitted",
                    "order_ccp_status": "Submitted",
                    "outsideRTH": False,
                    "origOrderType": "LIMIT",
                    "supportsTaxOpt": "1",
                    "lastExecutionTime": "260604183015",
                    "orderType": "Limit",
                    "bgColor": "#000000",
                    "fgColor": "#00F000",
                    "isEventTrading": "0",
                    "price": "15.51",
                    "timeInForce": "CLOSE",
                    "lastExecutionTime_r": 1780597815000,
                    "side": "BUY"
                }
            ]
        }
        
        orders = self.manager.list_live_orders(account_id="DU7126953")
        self.assertEqual(len(orders), 1)
        order = orders[0]
        
        # Verify fields and aliased fields
        self.assertEqual(order.orderId, 761319201)
        self.assertEqual(order.lmtPrice, 15.51) # parsed from alias 'price'
        self.assertEqual(order.cumFill, 0.0) # parsed from alias 'filledQuantity'
        
        # Verify extra fields are preserved in dump
        dump = order.model_dump()
        self.assertEqual(dump.get("companyName"), "ZIM INTEGRATED SHIPPING SERV")
        self.assertEqual(dump.get("secType"), "STK")
        self.assertEqual(dump.get("listingExchange"), "NYSE")

    def test_list_live_orders_new_api_format(self):
        # Mock response from the newer API version layout
        self.mock_client.get.return_value = {
            "orders": [
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
                    "acct": "DU12345"
                }
            ],
            "notifications": []
        }
        
        # Query with account matching
        orders = self.manager.list_live_orders(account_id="DU12345")
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].account, "DU12345")
        
        # Query with account non-matching
        orders_none = self.manager.list_live_orders(account_id="DU55555")
        self.assertEqual(len(orders_none), 0)

    def test_ensure_customer_order_id_generation(self):
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=10,
            price=150.0
            # no cId provided
        )
        c_id = self.manager._ensure_customer_order_id(request)
        self.assertIsNotNone(c_id)
        self.assertEqual(len(c_id), 18)

    def test_cancel_order_success(self):
        self.mock_client.delete.return_value = {"status": "cancelled"}
        res = self.manager.cancel_order("U123", "cust-123")
        self.assertEqual(res.get("status"), "cancelled")
        self.mock_client.delete.assert_called_with("/iserver/account/U123/order/cust-123")

    def test_place_order_failure(self):
        self.mock_client.post.side_effect = Exception("API Error")
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=10,
            cId="cust-123"
        )
        with self.assertRaises(Exception):
            self.manager.place_order("U123", request)

    def test_modify_order_failure(self):
        self.mock_client.post.side_effect = Exception("API Error")
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=10,
            cId="cust-123"
        )
        with self.assertRaises(Exception):
            self.manager.modify_order("U123", "1001", request)

    def test_cancel_order_failure(self):
        self.mock_client.delete.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.cancel_order("U123", "cust-123")

    def test_preview_orders_failure(self):
        self.mock_client.post.side_effect = Exception("API Error")
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=10
        )
        with self.assertRaises(Exception):
            self.manager.preview_orders("U123", request)

    def test_suppress_questions_failure(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.suppress_questions(["o163"])

    def test_reset_suppression_failure(self):
        self.mock_client.post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.reset_suppression()

    def test_get_order_status_failure(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_order_status("1001")

    def test_sync_orders_failure(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.sync_orders("U123")

    def test_get_questions_failure(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.get_questions()

    def test_list_live_orders_failure(self):
        self.mock_client.get.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            self.manager.list_live_orders("U123")

    def test_db_helpers_exception_handling(self):
        # Trigger exceptions in db calls to cover the exception handlers
        self.mock_db_manager.get_session.side_effect = Exception("DB Error")
        
        request = OrderRequest(
            conid=265598,
            orderType="LMT",
            side="BUY",
            quantity=10,
            cId="cust-db-error"
        )
        # These should log error and not crash
        self.manager._save_order_to_db("U123", request, "Submitted")
        self.manager._update_order_server_id("cust-db-error", "1001", "Submitted")
        self.manager._update_modified_order_in_db("cust-db-error", request, "Submitted")
    def test_modify_order_external(self):
        # Mock successful modification response
        self.mock_client.post.return_value = [
            {
                "order_id": "761319201",
                "order_status": "Submitted",
                "local_order_id": "761319201"
            }
        ]
        
        # When looking up customer_order_id, return None (simulating order not in DB)
        self.mock_session.execute.return_value.fetchone.return_value = None
        
        request = OrderRequest(
            conid=468091282,
            orderType="LMT",
            side="BUY",
            quantity=1000,
            price=14.21
        )
        
        results = self.manager.modify_order("DU7126953", "761319201", request)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].order_id, "761319201")
        self.assertEqual(request.cId, "761319201")
        self.assertEqual(request.acctId, "DU7126953")
        self.assertTrue(self.mock_session.execute.called)


class TestIBKROrdersCLI(unittest.TestCase):
    """
    Unit tests for the Orders CLI interface.
    """
    def setUp(self):
        self.manager_patcher = patch('tools.ibkr.ibkr_orders.cli.OrdersManager')
        self.mock_manager = self.manager_patcher.start()
        self.manager_instance = self.mock_manager.return_value
        
    def tearDown(self):
        self.manager_patcher.stop()

    def test_cli_place(self):
        from tools.ibkr.ibkr_orders.cli import main
        self.manager_instance.place_order.return_value = []
        with patch('sys.argv', ['ibkr_orders', 'place', '--account', 'U123', '--conid', '12345', '--side', 'BUY', '--type', 'LMT', '--qty', '10']):
            main()
            self.manager_instance.place_order.assert_called_once()

    def test_cli_modify_with_id_only(self):
        from tools.ibkr.ibkr_orders.cli import main
        self.manager_instance.modify_order.return_value = []
        with patch('sys.argv', ['ibkr_orders', 'modify', '--account', 'U123', '--id', '1001', '--conid', '12345', '--qty', '10', '--type', 'LMT']):
            main()
            self.manager_instance.modify_order.assert_called_once()

    def test_cli_modify_with_id_and_cid(self):
        from tools.ibkr.ibkr_orders.cli import main
        self.manager_instance.modify_order.reset_mock()
        self.manager_instance.modify_order.return_value = []
        with patch('sys.argv', ['ibkr_orders', 'modify', '--account', 'U123', '--id', '1001', '--cid', 'cust-123', '--conid', '12345', '--qty', '10', '--type', 'LMT']):
            main()
            self.manager_instance.modify_order.assert_called_once()

    def test_cli_cancel(self):
        from tools.ibkr.ibkr_orders.cli import main
        self.manager_instance.cancel_order.return_value = {}
        with patch('sys.argv', ['ibkr_orders', 'cancel', '--account', 'U123', '--cid', 'cust-123']):
            main()
            self.manager_instance.cancel_order.assert_called_once()

    def test_cli_list(self):
        from tools.ibkr.ibkr_orders.cli import main
        self.manager_instance.list_live_orders.return_value = []
        with patch('sys.argv', ['ibkr_orders', 'list', '--account', 'U123', '--filters', 'active', '--force']):
            main()
            self.manager_instance.list_live_orders.assert_called_once()

    def test_cli_preview(self):
        from tools.ibkr.ibkr_orders.cli import main
        mock_resp = MagicMock()
        mock_resp.model_dump.return_value = {}
        self.manager_instance.preview_orders.return_value = mock_resp
        with patch('sys.argv', ['ibkr_orders', 'preview', '--account', 'U123', '--conid', '12345', '--side', 'BUY', '--type', 'LMT', '--qty', '10']):
            main()
            self.manager_instance.preview_orders.assert_called_once()

    def test_cli_suppress(self):
        from tools.ibkr.ibkr_orders.cli import main
        self.manager_instance.suppress_questions.return_value = {}
        with patch('sys.argv', ['ibkr_orders', 'suppress', '--ids', 'o163', 'o10082']):
            main()
            self.manager_instance.suppress_questions.assert_called_once()

    def test_cli_suppress_reset(self):
        from tools.ibkr.ibkr_orders.cli import main
        self.manager_instance.reset_suppression.return_value = {}
        with patch('sys.argv', ['ibkr_orders', 'suppress-reset']):
            main()
            self.manager_instance.reset_suppression.assert_called_once()


if __name__ == "__main__":
    unittest.main()


