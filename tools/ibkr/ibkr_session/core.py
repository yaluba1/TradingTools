"""
Core logic for the IBKR Session tool.
This module provides the SessionManager class to interact with IBKR session endpoints
and persist session lifecycle data in a MariaDB database.
"""
import datetime
from typing import Optional, Dict, Any
from sqlalchemy import text
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..common.db_manager import db_manager
from ..schemas.session_schemas import AuthStatus, TickleResponse

class SessionManager:
    """
    Manager for IBKR Web API sessions.
    
    This class handles authentication status checks, session initialization,
    heartbeats (tickle), and termination, while maintaining a record of
    active sessions in the database.
    """
    def __init__(self):
        """
        Initialize the SessionManager.
        """
        self.tool_name = "session"
        self.client = IBKRClient(self.tool_name)
        self.logger = IBKRLogger(self.tool_name)

    def get_status(self) -> AuthStatus:
        """
        Retrieve the current authentication and connection status from the Gateway.
        
        This method also synchronizes the database's session records. If the API
        reports the session is no longer authenticated but the DB says it's ACTIVE,
        the DB record will be marked as EXPIRED.

        Returns:
            AuthStatus: Validated authentication status.
        """
        self.logger.info("Checking authentication status.")
        endpoint = "/iserver/auth/status"
        try:
            data = self.client.get(endpoint)
            status = AuthStatus(**data)
            
            # Synchronize database state with the API response
            self._sync_db_session(status.authenticated)
            
            self.logger.log_action(
                "get_status",
                message=f"Auth status: {'Authenticated' if status.authenticated else 'Not Authenticated'}, "
                        f"Connected: {'Yes' if status.connected else 'No'}"
            )
            return status
        except Exception as e:
            self.logger.error(f"Failed to check auth status: {e}")
            raise

    def init_session(self) -> Dict[str, Any]:
        """
        Request initialization of the brokerage session.
        
        If successful, a new entry is created in the 'ibkr_sessions' table.

        Returns:
            Dict[str, Any]: API response metadata.
        """
        self.logger.info("Initializing brokerage session.")
        endpoint = "/iserver/auth/ssodh/init"
        try:
            # We use post but the response for init is often metadata or empty
            data = self.client.post(endpoint)
            
            # Record the session start in the database
            self._record_session_start()
            
            self.logger.log_action("init_session", message="Brokerage session initialization initiated.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to initialize brokerage session: {e}")
            raise

    def logout(self) -> Dict[str, Any]:
        """
        Terminate the current session and update the database record.

        Returns:
            Dict[str, Any]: API response metadata.
        """
        self.logger.info("Logging out from IBKR Gateway.")
        endpoint = "/logout"
        try:
            data = self.client.post(endpoint)
            
            # Mark the active session as ended in the database
            self._record_session_end(status="LOGGED_OUT")
            
            self.logger.log_action("logout", message="Session logout completed.")
            return data
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            raise

    def tickle(self) -> TickleResponse:
        """
        Send a heartbeat to keep the session alive.

        Returns:
            TickleResponse: Validated tickle data.
        """
        self.logger.debug("Sending tickle heartbeat.")
        endpoint = "/tickle"
        try:
            data = self.client.post(endpoint)
            response = TickleResponse(**data)
            return response
        except Exception as e:
            self.logger.error(f"Tickle failed: {e}")
            raise

    def reauthenticate(self) -> Dict[str, Any]:
        """
        Trigger session re-authentication.

        Returns:
            Dict[str, Any]: API response metadata.
        """
        self.logger.info("Requesting session re-authentication.")
        endpoint = "/iserver/reauthenticate"
        try:
            data = self.client.post(endpoint)
            self.logger.log_action("reauthenticate", message="Re-authentication requested.")
            return data
        except Exception as e:
            self.logger.error(f"Re-authentication failed: {e}")
            raise

    def _sync_db_session(self, api_authenticated: bool):
        """
        Synchronize the database state with the actual API status.
        If the DB thinks there is an active session but the API says no,
        mark the DB record as EXPIRED.
        """
        if not api_authenticated:
            # Check if we have an ACTIVE session that should be marked EXPIRED
            self._record_session_end(status="EXPIRED")

    def _record_session_start(self):
        """
        Insert a new record into ibkr_sessions. 
        Ensures only one session is 'ACTIVE' at a time.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            with db_manager.get_session() as session:
                # First, ensure any dangling active sessions are closed
                session.execute(text("""
                    UPDATE ibkr_sessions 
                    SET end_time_utc = :now, status = 'SUPERSEDED' 
                    WHERE status = 'ACTIVE'
                """), {"now": now})
                
                # Insert the new active session
                session.execute(text("""
                    INSERT INTO ibkr_sessions (start_time_utc, status) 
                    VALUES (:now, 'ACTIVE')
                """), {"now": now})
        except Exception as e:
            self.logger.error(f"Failed to record session start in database: {e}")

    def _record_session_end(self, status: str = "LOGGED_OUT"):
        """
        Update the latest ACTIVE session record with an end time and new status.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            with db_manager.get_session() as session:
                session.execute(text("""
                    UPDATE ibkr_sessions 
                    SET end_time_utc = :now, status = :status 
                    WHERE status = 'ACTIVE'
                """), {"now": now, "status": status})
        except Exception as e:
            self.logger.error(f"Failed to record session end in database: {e}")
