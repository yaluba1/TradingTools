"""
Logging utility for IBKR Trading Tools.
This module provides a dual-logging system that writes logs to a local file
and also records main actions in a MariaDB database table.
"""
import logging
import datetime
import json
from pathlib import Path
from typing import Optional, Any, Dict
from sqlalchemy import text
from .config import get_ibkr_config
from .db_manager import db_manager

class IBKRLogger:
    """
    Custom logger that handles file output and database logging.
    
    This class wraps the standard logging module and adds functionality to
    persist main actions (INFO and ERROR levels) to a MariaDB table.
    """
    def __init__(self, tool_name: str):
        """
        Initialize the logger for a specific tool.

        Args:
            tool_name (str): The name of the tool (e.g., 'alerts', 'orders') 
                             used to identify logs.
        """
        self.tool_name = tool_name
        config = get_ibkr_config()
        
        # Determine the log file path, expanding the home directory if necessary.
        log_file_str = config["logging"]["file_path"]
        if log_file_str.startswith("~"):
            log_file = Path.home() / log_file_str[2:]
        else:
            log_file = Path(log_file_str)
            
        # Ensure the parent directory for the log file exists.
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Set the logging level based on the configuration.
        log_level_str = config["logging"].get("level", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        self.logger = logging.getLogger(f"ibkr.{tool_name}")
        self.logger.setLevel(log_level)
        
        # Configure handlers only if they haven't been added yet (singleton-like).
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # File Handler: writes to the local log file.
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            # Console Handler: useful for real-time feedback during CLI usage.
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_action(self, action: str, level: str = "INFO", message: str = "", 
                   account_id: Optional[str] = None, alert_id: Optional[str] = None, 
                   details: Optional[Dict[str, Any]] = None):
        """
        Log an action to the file handler and the database.

        Args:
            action (str): The name of the action being performed.
            level (str): Logging level ('INFO', 'DEBUG', 'ERROR', 'WARNING').
            message (str): A descriptive message for the log.
            account_id (Optional[str]): The relevant account identifier.
            alert_id (Optional[str]): The relevant alert or order identifier.
            details (Optional[Dict[str, Any]]): Additional metadata to log as JSON.
        """
        log_msg = f"[{action}] {message}"
        if account_id:
            log_msg += f" (Account: {account_id})"
        if alert_id:
            log_msg += f" (Alert: {alert_id})"
            
        # Log to the standard logging system (file/console)
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(log_msg)
        
        # Main actions (INFO, ERROR) are also persisted to the MariaDB logs table.
        if level.upper() in ["INFO", "ERROR"]:
            self._log_to_db(action, level, message, account_id, alert_id, details)

    def _log_to_db(self, action: str, level: str, message: str, 
                   account_id: Optional[str], alert_id: Optional[str], 
                   details: Optional[Dict[str, Any]]):
        """
        Insert a log entry into the MariaDB 'ibkr_logs' table.

        Args:
            action (str): The action name.
            level (str): The log level.
            message (str): The descriptive message.
            account_id (Optional[str]): Account ID.
            alert_id (Optional[str]): Alert/Order ID.
            details (Optional[Dict[str, Any]]): JSON-serializable metadata.
        """
        # Always use UTC time for database logs as per requirements.
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        try:
            with db_manager.get_session() as session:
                query = text("""
                    INSERT INTO ibkr_logs 
                    (timestamp_utc, tool_name, action, account_id, alert_id, level, message, details)
                    VALUES (:ts, :tool, :act, :acc, :aid, :lvl, :msg, :det)
                """)
                
                det_json = json.dumps(details) if details else None
                
                session.execute(query, {
                    "ts": timestamp,
                    "tool": self.tool_name,
                    "act": action,
                    "acc": account_id,
                    "aid": alert_id,
                    "lvl": level,
                    "msg": message,
                    "det": det_json
                })
        except Exception as e:
            # Fallback: if database logging fails, record the failure in the file log.
            self.logger.error(f"Failed to log to database: {e}")

    # Wrappers for standard logging methods for convenience
    def info(self, msg, *args, **kwargs): self.logger.info(msg, *args, **kwargs)
    def debug(self, msg, *args, **kwargs): self.logger.debug(msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs): self.logger.error(msg, *args, **kwargs)
    def warning(self, msg, *args, **kwargs): self.logger.warning(msg, *args, **kwargs)
