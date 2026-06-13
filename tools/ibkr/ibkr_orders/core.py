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
    OrderReplyRequest, LiveOrder, SyncOrderResult, QuestionInfo,
    WhatIfResponse, SuppressRepliesRequest
)

def normalize_filters(filters_str: str) -> str:
    """
    Normalizes the casing of order filter query parameters to match IBKR expectations.
    For example, 'submitted' -> 'Submitted', 'filled' -> 'Filled'.
    Supports comma-separated values.
    """
    mapping = {
        "active": "active",
        "submitted": "Submitted",
        "filled": "Filled",
        "cancelled": "Cancelled",
        "inactive": "Inactive",
        "pending_submit": "PendingSubmit",
        "pendingsubmit": "PendingSubmit",
        "presubmitted": "PreSubmitted",
        "pre_submitted": "PreSubmitted",
        "warn_state": "WarnState",
        "warnstate": "WarnState"
    }
    parts = [p.strip() for p in filters_str.split(",")]
    normalized_parts = []
    for part in parts:
        part_lower = part.lower()
        if part_lower in mapping:
            normalized_parts.append(mapping[part_lower])
        else:
            normalized_parts.append(part.title())
    return ",".join(normalized_parts)

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

    def _extract_orders(self, data: Any) -> List[Dict[str, Any]]:
        """
        Extracts a flat list of raw order dictionaries from the gateway response.
        Handles both the current "orders" array format and the legacy account-keyed format.
        """
        raw_orders = []
        if isinstance(data, dict):
            if "orders" in data and isinstance(data["orders"], list):
                raw_orders = data["orders"]
            else:
                for acc_key, orders_list in data.items():
                    if isinstance(orders_list, list):
                        # Ensure each order dict has the account key mapped
                        for o in orders_list:
                            if isinstance(o, dict) and "account" not in o and "acct" not in o:
                                o["account"] = acc_key
                        raw_orders.extend(orders_list)
        elif isinstance(data, list):
            raw_orders = data
        return raw_orders

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
        request.acctId = request.acctId or account_id
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

            final_results = self._process_order_placement_results(
                c_id=c_id,
                results=results,
                auto_confirm=auto_confirm,
                success_event_type="ORDER_PLACED_SUCCESS"
            )

            self.logger.log_action(
                "place_order",
                account_id=account_id,
                message=f"Successfully placed {request.side} order for {request.quantity} contract(s).",
                details={"cId": c_id, "results": [r.model_dump() for r in final_results]}
            )
            return final_results
        except Exception as e:
            self.logger.log_action(
                "place_order",
                account_id=account_id,
                level="ERROR",
                message=f"Failed to place order {c_id}: {e}",
                details={"cId": c_id}
            )
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

    def _process_order_placement_results(
        self, 
        c_id: str, 
        results: List[OrderPlacementResponse], 
        auto_confirm: bool, 
        success_event_type: str
    ) -> List[OrderPlacementResponse]:
        """
        Process the results of order placement or modification.
        If auto_confirm is True, replies to any warning messages and recursively processes replies.
        Updates the database order record and logs events when a final order acceptance is found.
        """
        final_results = []
        for res in results:
            if res.id and auto_confirm:
                self.logger.info(f"Auto-confirming IBKR warning for order {c_id}: {res.message}")
                try:
                    confirm_res = self.reply_to_question(res.id, True)
                    processed_confirm_res = self._process_order_placement_results(
                        c_id=c_id,
                        results=confirm_res,
                        auto_confirm=auto_confirm,
                        success_event_type=success_event_type
                    )
                    final_results.extend(processed_confirm_res)
                except Exception as e:
                    self.logger.error(f"Failed to auto-confirm warning {res.id}: {e}")
                    final_results.append(res)
            else:
                final_results.append(res)
                if res.order_id:
                    self._update_order_server_id(c_id, res.order_id, res.order_status)
                    if success_event_type == "ORDER_MODIFY_SUCCESS":
                        msg = f"Order modification accepted by IBKR: status {res.order_status}"
                    else:
                        msg = f"Order accepted by IBKR with server ID {res.order_id}"
                    self._log_order_event(c_id, success_event_type, msg, res.model_dump())
        return final_results

    def cancel_order(self, account_id: str, c_id: str) -> Dict[str, Any]:
        """
        Request cancellation of an order.
        
        Args:
            account_id (str): Account identifier.
            c_id (str): Customer order identifier (cId).
        """
        self.logger.info(f"Cancelling order {c_id} on account {account_id}")
        endpoint = f"/iserver/account/{account_id}/order/{c_id}"
        
        resolved_c_id = self._find_customer_order_id(c_id)
        
        try:
            data = self.client.delete(endpoint)
            if resolved_c_id:
                self._log_order_event(resolved_c_id, "CANCEL_REQUESTED", "Cancellation request sent to IBKR", data)
            self.logger.log_action(
                "cancel_order",
                account_id=account_id,
                message=f"Successfully requested cancellation of order {c_id}.",
                details={"cId": c_id, "response": data}
            )
            return data
        except Exception as e:
            self.logger.log_action(
                "cancel_order",
                account_id=account_id,
                level="ERROR",
                message=f"Failed to cancel order {c_id}: {e}",
                details={"cId": c_id}
            )
            raise

    def modify_order(self, account_id: str, order_id: str, request: OrderRequest, auto_confirm: bool = False) -> List[OrderPlacementResponse]:
        """
        Modify an existing open order.
        
        Args:
            account_id (str): IBKR account identifier.
            order_id (str): The unique ID of the order to modify (server order ID or customer order ID).
            request (OrderRequest): The updated order details.
            auto_confirm (bool): If True, automatically replies 'yes' to IBKR warnings.
        
        Returns:
            List[OrderPlacementResponse]: Results from IBKR, which may include questions/prompts.
        """
        request.acctId = request.acctId or account_id
        
        # Resolve the customer order ID from the database
        resolved_c_id = self._find_customer_order_id(order_id)
        if not resolved_c_id:
            # Order not in database yet (e.g., placed externally).
            # We use request.cId if specified, otherwise we use order_id as the fallback customer_order_id.
            resolved_c_id = request.cId or order_id
            request.cId = resolved_c_id
            self._save_order_to_db(account_id, request, "PendingSubmit", server_order_id=order_id)
        else:
            # Use the existing resolved customer order ID
            if not request.cId:
                request.cId = resolved_c_id

        self.logger.info(f"Modifying order {order_id} on account {account_id} with new parameters: {request.model_dump()}")
        
        endpoint = f"/iserver/account/{account_id}/order/{order_id}"
        payload = request.model_dump()
        
        try:
            data = self.client.post(endpoint, json_data=payload)
            results = OrderPlacementResults.model_validate(data).root
            
            # Database record update and log event
            self._update_modified_order_in_db(resolved_c_id, request, "PendingSubmit")
            self._log_order_event(resolved_c_id, "ORDER_MODIFY_REQUEST", f"Modify request sent for order {order_id}", payload)

            final_results = self._process_order_placement_results(
                c_id=resolved_c_id,
                results=results,
                auto_confirm=auto_confirm,
                success_event_type="ORDER_MODIFY_SUCCESS"
            )
            
            self.logger.log_action(
                "modify_order",
                account_id=account_id,
                message=f"Successfully requested modification of order {order_id}.",
                details={"order_id": order_id, "results": [r.model_dump() for r in final_results]}
            )
            return final_results
        except Exception as e:
            self.logger.log_action(
                "modify_order",
                account_id=account_id,
                level="ERROR",
                message=f"Failed to modify order {order_id}: {e}",
                details={"order_id": order_id}
            )
            self._log_order_event(resolved_c_id, "ORDER_MODIFY_FAILED", str(e))
            raise

    def preview_orders(self, account_id: str, request: OrderRequest) -> WhatIfResponse:
        """
        Preview the projected effects of an order ticket (What-If scenario) on the account.
        
        Args:
            account_id (str): IBKR account identifier.
            request (OrderRequest): The order details to preview.
            
        Returns:
            WhatIfResponse: The projected margin and commission changes.
        """
        request.acctId = request.acctId or account_id
        self.logger.info(f"Previewing order effects (What-If) for account {account_id}")
        endpoint = f"/iserver/account/{account_id}/orders/whatif"
        payload = {"orders": [request.model_dump()]}
        
        try:
            data = self.client.post(endpoint, json_data=payload)
            response = WhatIfResponse.model_validate(data)
            self.logger.log_action(
                "preview_orders",
                account_id=account_id,
                message="Successfully previewed order effects (What-If).",
                details={"conid": request.conid, "qty": request.quantity}
            )
            return response
        except Exception as e:
            self.logger.log_action(
                "preview_orders",
                account_id=account_id,
                level="ERROR",
                message=f"Failed to preview order: {e}",
                details={"conid": request.conid}
            )
            raise

    def suppress_questions(self, message_ids: List[str]) -> Dict[str, Any]:
        """
        Suppress specific order reply warning messages for the remainder of the session.
        
        Args:
            message_ids (List[str]): List of message/warning IDs to suppress (e.g., 'o163').
            
        Returns:
            Dict[str, Any]: The API response.
        """
        self.logger.info(f"Requesting suppression of messages: {message_ids}")
        endpoint = "/iserver/questions/suppress"
        payload = {"messageIds": message_ids}
        
        try:
            data = self.client.post(endpoint, json_data=payload)
            return data
        except Exception as e:
            self.logger.error(f"Failed to suppress messages: {e}")
            raise

    def reset_suppression(self) -> Dict[str, Any]:
        """
        Reset the suppression of all order reply/warning messages.
        
        Returns:
            Dict[str, Any]: The API response.
        """
        self.logger.info("Resetting order reply message suppressions")
        endpoint = "/iserver/questions/suppress/reset"
        
        try:
            data = self.client.post(endpoint)
            return data
        except Exception as e:
            self.logger.error(f"Failed to reset suppressions: {e}")
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
            raw_orders = self._extract_orders(data)
            
            results = []
            
            # 2. Iterate through live orders
            for o_data in raw_orders:
                live_order = LiveOrder.model_validate(o_data)
                if account_id and live_order.account != account_id:
                    continue
                
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

    def list_live_orders(
        self,
        account_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        filters: Optional[str] = None,
        force: bool = False
    ) -> List[LiveOrder]:
        """
        Retrieve a list of live orders, optionally filtered.
        
        Args:
            account_id (Optional[str]): Account identifier.
            status_filter (Optional[str]): Optional status to filter by (e.g., 'Filled', 'Submitted').
            filters (Optional[str]): Optional order status query filter (e.g. 'filled', 'active').
            force (bool): If True, forces a refresh of the order status.
        """
        self.logger.info(f"Listing live orders (acc={account_id}, filter={status_filter}, filters={filters}, force={force})")
        endpoint = "/iserver/account/orders"
        params = {}
        if account_id:
            params["accountId"] = account_id
        
        # Determine the query filters parameter
        api_filters = filters
        if not api_filters and status_filter:
            status_clean = status_filter.lower().replace("_", "").replace(" ", "")
            # Map clean status strings to known filter values expected by the API client
            status_to_filter = {
                "active": "active",
                "submitted": "submitted",
                "filled": "filled",
                "cancelled": "cancelled",
                "inactive": "inactive",
                "pendingsubmit": "pending_submit",
                "presubmitted": "presubmitted",
                "warnstate": "warn_state"
            }
            if status_clean in status_to_filter:
                api_filters = status_to_filter[status_clean]
        
        if api_filters:
            params["filters"] = normalize_filters(api_filters)
            
        if force:
            params["force"] = "true"

        try:
            data = self.client.get(endpoint, params=params)
            raw_orders = self._extract_orders(data)
            
            all_orders = []
            for o_data in raw_orders:
                order = LiveOrder.model_validate(o_data)
                if account_id and order.account != account_id:
                    continue
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

    def _find_customer_order_id(self, identifier: str) -> Optional[str]:
        """
        Locates the customer_order_id in the database for a given identifier,
        which can be either the customer_order_id itself or the server_order_id.
        """
        try:
            with db_manager.get_session() as session:
                query = text("""
                    SELECT customer_order_id FROM ibkr_orders 
                    WHERE customer_order_id = :id OR server_order_id = :id
                """)
                row = session.execute(query, {"id": identifier}).fetchone()
                if row:
                    return row[0]
        except Exception as e:
            self.logger.error(f"DB Error looking up customer order ID for {identifier}: {e}")
        return None

    def _save_order_to_db(self, account_id: str, request: OrderRequest, status: str, server_order_id: Optional[str] = None):
        """
        Inserts or updates the primary order record in ibkr_orders.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            with db_manager.get_session() as session:
                query = text("""
                    INSERT INTO ibkr_orders 
                    (customer_order_id, server_order_id, account_id, conid, side, order_type, quantity, price, aux_price, tif, status, last_update_utc, created_at_utc)
                    VALUES (:cid, :sid, :acc, :con, :side, :type, :qty, :prc, :aux, :tif, :status, :utc, :utc)
                    ON DUPLICATE KEY UPDATE 
                    status = :status, last_update_utc = :utc, server_order_id = COALESCE(:sid, server_order_id)
                """)
                session.execute(query, {
                    "cid": request.cId,
                    "sid": server_order_id,
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

    def _update_modified_order_in_db(self, c_id: str, request: OrderRequest, status: str):
        """
        Updates the order details in the database after a modification request.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            with db_manager.get_session() as session:
                query = text("""
                    UPDATE ibkr_orders 
                    SET quantity = :qty, price = :prc, aux_price = :aux, tif = :tif, status = :status, last_update_utc = :utc
                    WHERE customer_order_id = :cid OR server_order_id = :cid
                """)
                session.execute(query, {
                    "cid": c_id,
                    "qty": request.quantity,
                    "prc": request.price,
                    "aux": request.auxPrice,
                    "tif": request.tif,
                    "status": status,
                    "utc": now
                })
        except Exception as e:
            self.logger.error(f"DB Error updating modified order {c_id}: {e}")

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
