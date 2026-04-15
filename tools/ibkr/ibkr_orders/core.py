"""
Core logic for the IBKR Orders tool.
This module implements the OrdersManager class, which handles the lifecycle
of orders including placement, modification, cancellation, and synchronization
between the IBKR Gateway and the local MariaDB database.
"""
import time
import json
import uuid
import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import text
from ..common.api_client import IBKRClient
from ..common.db_manager import db_manager
from ..common.logger import IBKRLogger
from ..schemas.order_schemas import (
    OrderRequest, OrderPlacementResponse, OrderPlacementResults,
    OrderReplyRequest, LiveOrder, SyncOrderResult, QuestionInfo
)

class OrdersManager:
    """
    Manager for coordinating IBKR Order operations.
    Provides methods to interact with the /iserver/account/order endpoints
    while maintaining a persistent state in the database.
    """
    def __init__(self):
        """
        Initialize the OrdersManager with an IBKR API client and logger.
        """
        self.client = IBKRClient("orders")
        self.logger = self.client.logger

    def _ensure_customer_order_id(self, request: OrderRequest) -> str:
        """
        Ensure the request has a unique customer order ID (cId).
        If not provided, generates a UUID.
        """
        if not request.cId:
            request.cId = str(uuid.uuid4())[:18] # IBKR cId limit is usually 30chars
        return request.cId

    def place_order(self, account_id: str, request: OrderRequest, auto_confirm: bool = False) -> List[OrderPlacementResponse]:
        """
        Place a new order for a specific account.
        
        Args:
            account_id (str): IBKR account identifier.
            request (OrderRequest): The order details.
            auto_confirm (bool): If True, automatically replies 'yes' to IBKR warnings.
        
        Returns:
            List[OrderPlacementResponse]: Results from IBKR, which may include questions.
        """
        c_id = self._ensure_customer_order_id(request)
        self.logger.info(f"Placing {request.side} order for {request.quantity} {request.secType} on account {account_id} (cId: {c_id})")
        
        endpoint = f"/iserver/account/{account_id}/orders"
        payload = {"orders": [request.model_dump()]}
        
        try:
            data = self.client.post(endpoint, json_data=payload)
            results = OrderPlacementResults.model_validate(data).root
            
            # Initial database record creation
            self._save_order_to_db(account_id, request, "PendingSubmit")
            self._log_order_event(c_id, "ORDER_PLACED_REQUEST", f"Initial placement request sent: {request.side} {request.quantity}", payload)

            final_results = []
            for res in results:
                # Handle confirmations/questions if auto_confirm is enabled
                if res.id and auto_confirm:
                    self.logger.info(f"Auto-confirming IBKR warning for order {c_id}: {res.message}")
                    confirm_res = self.reply_to_question(res.id, True)
                    # Recursively handle the next response if it's still a question (though usually it's one level)
                    # For simplicity in this tool, we just log and return the confirmation result.
                    final_results.extend(confirm_res)
                else:
                    final_results.append(res)
                    if res.order_id:
                        self._update_order_server_id(c_id, res.order_id, res.order_status)
                        self._log_order_event(c_id, "ORDER_PLACED_SUCCESS", f"Order accepted by IBKR with server ID {res.order_id}", res.model_dump())

            return final_results
        except Exception as e:
            self.logger.error(f"Failed to place order {c_id}: {e}")
            self._log_order_event(c_id, "ORDER_PLACEMENT_FAILED", str(e))
            raise

    def reply_to_question(self, reply_id: str, confirmed: bool) -> List[OrderPlacementResponse]:
        """
        Reply to a confirmation question from IBKR.
        
        Args:
            reply_id (str): The ID of the question to answer.
            confirmed (bool): True to agree, False to cancel.
        """
        endpoint = f"/iserver/reply/{reply_id}"
        payload = {"confirmed": confirmed}
        self.logger.info(f"Replying to question {reply_id} (confirmed={confirmed})")
        
        try:
            data = self.client.post(endpoint, json_data=payload)
            return OrderPlacementResults.model_validate(data).root
        except Exception as e:
            self.logger.error(f"Failed to reply to question {reply_id}: {e}")
            raise

    def cancel_order(self, account_id: str, c_id: str) -> Dict[str, Any]:
        """
        Request cancellation of an order.
        
        Args:
            account_id (str): Account identifier.
            c_id (str): Customer order identifier (cId).
        """
        self.logger.info(f"Cancelling order {c_id} on account {account_id}")
        endpoint = f"/iserver/account/{account_id}/order/{c_id}"
        
        try:
            data = self.client.delete(endpoint)
            self._log_order_event(c_id, "CANCEL_REQUESTED", "Cancellation request sent to IBKR", data)
            return data
        except Exception as e:
            self.logger.error(f"Failed to cancel order {c_id}: {e}")
            raise

    def sync_orders(self, account_id: Optional[str] = None) -> List[SyncOrderResult]:
        """
        Synchronize the local database state with live orders from IBKR.
        
        Args:
            account_id (Optional[str]): Specific account to sync. If None, syncs all.
        """
        self.logger.info(f"Syncing orders {'for all accounts' if not account_id else f'for account {account_id}'}")
        
        # 1. Fetch live orders from IBKR
        endpoint = "/iserver/account/orders"
        try:
            data = self.client.get(endpoint)
            # IBKR returns a dict where keys are account IDs and values are lists of orders.
            live_orders_map = data if isinstance(data, dict) else {}
            
            results = []
            
            # 2. Iterate through live orders
            for acc_id, orders in live_orders_map.items():
                if account_id and acc_id != account_id:
                    continue
                
                for o_data in orders:
                    live_order = LiveOrder.model_validate(o_data)
                    # Note: IBKR doesn't always return the cId in /orders, but it might be in some versions.
                    # We might need to match by server orderId if cId is missing.
                    res = self._sync_single_order(live_order)
                    if res:
                        results.append(res)
            
            # 3. Handle orders that are in DB but NOT in live list (they might be filled or cancelled)
            # This is complex because /orders only shows live ones. We'd need /history for others.
            # For now, we focus on updating live ones.
            
            return results
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            raise

    def get_questions(self) -> List[QuestionInfo]:
        """
        Retrieve all active questions or prompts from IBKR that require a response.
        
        Returns:
            List[QuestionInfo]: A list of pending questions.
        """
        self.logger.info("Fetching active questions from IBKR")
        endpoint = "/iserver/questions"
        try:
            data = self.client.get(endpoint)
            # IBKR usually returns a list of question objects
            if not isinstance(data, list):
                return []
            return [QuestionInfo.model_validate(q) for q in data]
        except Exception as e:
            self.logger.error(f"Failed to fetch questions: {e}")
            raise

    def get_order_status(self, order_id: str) -> LiveOrder:
        """
        Retrieve the status of a specific order.
        
        Args:
            order_id (str): The server order ID or customer order ID.
        """
        self.logger.info(f"Fetching status for order {order_id}")
        endpoint = f"/iserver/account/order/status/{order_id}"
        try:
            data = self.client.get(endpoint)
            return LiveOrder.model_validate(data)
        except Exception as e:
            self.logger.error(f"Failed to fetch order status for {order_id}: {e}")
            raise

    def list_live_orders(self, account_id: Optional[str] = None, status_filter: Optional[str] = None) -> List[LiveOrder]:
        """
        Retrieve a list of live orders, optionally filtered.
        
        Args:
            account_id (Optional[str]): Account identifier.
            status_filter (Optional[str]): Optional status to filter by (e.g., 'Filled', 'Submitted').
        """
        self.logger.info(f"Listing live orders (acc={account_id}, filter={status_filter})")
        endpoint = "/iserver/account/orders"
        try:
            data = self.client.get(endpoint)
            live_orders_map = data if isinstance(data, dict) else {}
            
            all_orders = []
            for acc_id, orders in live_orders_map.items():
                if account_id and acc_id != account_id:
                    continue
                for o_data in orders:
                    order = LiveOrder.model_validate(o_data)
                    if status_filter and status_filter.lower() not in order.status.lower():
                        continue
                    all_orders.append(order)
            
            return all_orders
        except Exception as e:
            self.logger.error(f"Failed to list live orders: {e}")
            raise

    def run_background_sync(self, interval_seconds: int = 60, account_id: Optional[str] = None):
        """
        Run a continuous synchronization loop.
        Useful for standalone tracking agents.
        """
        self.logger.info(f"Starting background sync loop every {interval_seconds}s")
        try:
            while True:
                try:
                    sync_results = self.sync_orders(account_id)
                    if sync_results:
                        self.logger.info(f"Synced {len(sync_results)} order updates.")
                except Exception as e:
                    self.logger.error(f"Error in sync loop: {e}")
                
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            self.logger.info("Background sync loop stopped by user.")

    # --- Database Helpers ---

    def _save_order_to_db(self, account_id: str, request: OrderRequest, status: str):
        """
        Inserts or updates the primary order record in ibkr_orders.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            with db_manager.get_session() as session:
                query = text("""
                    INSERT INTO ibkr_orders 
                    (customer_order_id, account_id, conid, side, order_type, quantity, price, aux_price, tif, status, last_update_utc, created_at_utc)
                    VALUES (:cid, :acc, :con, :side, :type, :qty, :prc, :aux, :tif, :status, :utc, :utc)
                    ON DUPLICATE KEY UPDATE 
                    status = :status, last_update_utc = :utc
                """)
                session.execute(query, {
                    "cid": request.cId,
                    "acc": account_id,
                    "con": request.conid,
                    "side": request.side,
                    "type": request.orderType,
                    "qty": request.quantity,
                    "prc": request.price,
                    "aux": request.auxPrice,
                    "tif": request.tif,
                    "status": status,
                    "utc": now
                })
        except Exception as e:
            self.logger.error(f"DB Error saving order {request.cId}: {e}")

    def _update_order_server_id(self, c_id: str, server_id: str, status: Optional[str]):
        """
        Updates the server-assigned order ID in the database.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            with db_manager.get_session() as session:
                query = text("""
                    UPDATE ibkr_orders 
                    SET server_order_id = :sid, status = COALESCE(:status, status), last_update_utc = :utc
                    WHERE customer_order_id = :cid
                """)
                session.execute(query, {"cid": c_id, "sid": server_id, "status": status, "utc": now})
        except Exception as e:
            self.logger.error(f"DB Error updating server ID for {c_id}: {e}")

    def _log_order_event(self, c_id: str, event_type: str, message: str, data: Any = None):
        """
        Records a lifecycle event in ibkr_order_events.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            det_json = json.dumps(data) if data else None
            with db_manager.get_session() as session:
                query = text("""
                    INSERT INTO ibkr_order_events (customer_order_id, event_type, timestamp_utc, data, message)
                    VALUES (:cid, :type, :utc, :data, :msg)
                """)
                session.execute(query, {
                    "cid": c_id,
                    "type": event_type,
                    "utc": now,
                    "data": det_json,
                    "msg": message
                })
        except Exception as e:
            self.logger.error(f"DB Error logging event for {c_id}: {e}")

    def _sync_single_order(self, live_order: LiveOrder) -> Optional[SyncOrderResult]:
        """
        Synchronizes a single live order from IBKR with the local DB.
        """
        # We need to find the c_id. Unfortunately IBKR live monitor often lacks c_id.
        # We fall back to finding by server-order-id.
        s_id = str(live_order.orderId)
        
        try:
            with db_manager.get_session() as session:
                query = text("SELECT customer_order_id, status, filled_quantity FROM ibkr_orders WHERE server_order_id = :sid OR customer_order_id = :sid")
                row = session.execute(query, {"sid": s_id}).fetchone()
                
                if not row:
                    # Order exists in IBKR but not in our DB? 
                    # Maybe it was placed elsewhere. We could import it, but for now we skip or log.
                    return None
                
                c_id, old_status, old_filled = row
                
                status_changed = old_status != live_order.status
                filled_increment = live_order.cumFill - float(old_filled)
                
                if status_changed or filled_increment > 0:
                    now = datetime.datetime.now(datetime.timezone.utc)
                    update_query = text("""
                        UPDATE ibkr_orders 
                        SET status = :status, filled_quantity = :filled, avg_fill_price = :avg, last_update_utc = :utc
                        WHERE customer_order_id = :cid
                    """)
                    session.execute(update_query, {
                        "status": live_order.status,
                        "filled": live_order.cumFill,
                        "avg": live_order.avgPrice,
                        "utc": now,
                        "cid": c_id
                    })
                    
                    event_type = "STATUS_SYNC"
                    if filled_increment > 0:
                        event_type = "FILL" if live_order.status == "Filled" else "PARTIAL_FILL"
                    
                    msg = f"Synced update: {live_order.status}, Filled: {live_order.cumFill}"
                    self._log_order_event(c_id, event_type, msg, live_order.model_dump())
                    
                    return SyncOrderResult(
                        customer_order_id=c_id,
                        status_changed=status_changed,
                        old_status=old_status,
                        new_status=live_order.status,
                        filled_increment=filled_increment,
                        event_logged=True
                    )
            return None
        except Exception as e:
            self.logger.error(f"Error syncing order {s_id}: {e}")
            return None
