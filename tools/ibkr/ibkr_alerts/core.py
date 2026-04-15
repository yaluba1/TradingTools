"""
Core business logic for the IBKR Alerts tool.
This module implements the AlertsManager class, which facilitates high-level 
operations like listing, creating, modifying, and deactivating IBKR alerts.
"""
from typing import List, Optional, Dict, Any
from ..common.api_client import IBKRClient
from ..common.logger import IBKRLogger
from ..schemas.alert_schemas import (
    AlertCreateRequest, AlertResponse, AlertListItem, AlertDetails
)

class AlertsManager:
    """
    Manager for coordinate IBKR Alerts operations.
    
    This class provide clean methods to interact with the IBKR API for 
    alerts-related tasks, handling authentication and logging automatically.
    """
    def __init__(self):
        """
        Initialize the AlertsManager with an IBKR API client for the 'alerts' tool.
        """
        self.client = IBKRClient("alerts")
        self.logger = self.client.logger

    def list_alerts(self, account_id: str) -> List[AlertListItem]:
        """
        Retrieve a list of all alerts associated with the given account.

        Args:
            account_id (str): The account identifier (e.g., 'DU1234567').

        Returns:
            List[AlertListItem]: A list of alert summaries.

        Raises:
            Exception: If the API request fails or the response is invalid.
        """
        self.logger.info(f"Listing alerts for account {account_id}")
        endpoint = f"/iserver/account/{account_id}/alerts"
        try:
            # Perform a GET request to the IBKR Gateway.
            data = self.client.get(endpoint)
            # Parse the response data into Pydantic models.
            alerts = [AlertListItem(**item) for item in data]
            
            # Log the successful action to the database.
            self.logger.log_action(
                "list_alerts", 
                message=f"Retrieved {len(alerts)} alerts", 
                account_id=account_id
            )
            return alerts
        except Exception as e:
            self.logger.error(f"Failed to list alerts: {e}")
            raise

    def get_alert_details(self, alert_id: int) -> AlertDetails:
        """
        Fetch the full details of a specific alert by its ID.

        Args:
            alert_id (int): The unique order/alert ID from IBKR.

        Returns:
            AlertDetails: A model containing the alert's configuration and conditions.

        Raises:
            Exception: If the update fails.
        """
        self.logger.info(f"Fetching details for alert {alert_id}")
        # The query parameter 'type=Q' is required per IBKR documentation.
        endpoint = f"/iserver/account/alert/{alert_id}"
        try:
            data = self.client.get(endpoint, params={"type": "Q"})
            # Validate and parse the JSON response.
            details = AlertDetails(**data)
            
            self.logger.log_action(
                "get_alert", 
                message=f"Retrieved details for alert {alert_id}", 
                alert_id=str(alert_id)
            )
            return details
        except Exception as e:
            self.logger.error(f"Failed to get alert details for {alert_id}: {e}")
            raise

    def create_or_modify_alert(self, account_id: str, request: AlertCreateRequest) -> AlertResponse:
        """
        Create a new alert or modify an existing one if the name already exists.

        This method implements the idempotency strategy: if an alert with the 
        same name exists for the account, it is updated; otherwise, a new one 
        is created.

        Args:
            account_id (str): Account ID.
            request (AlertCreateRequest): The desired alert configuration.

        Returns:
            AlertResponse: Status of the creation or modification.
        """
        self.logger.info(f"Ensuring alert '{request.alertName}' is present.")
        
        # 1. Check for existing alerts with the same name.
        existing_alerts = self.list_alerts(account_id)
        existing_alert = next((a for a in existing_alerts if a.alert_name == request.alertName), None)
        
        endpoint = f"/iserver/account/{account_id}/alert"
        payload = request.model_dump()
        
        if existing_alert:
            # Modification path: include the existing ID in the request body.
            self.logger.info(f"Alert '{request.alertName}' found (ID: {existing_alert.order_id}). Modifying...")
            payload["alertId"] = existing_alert.order_id
            action = "modify_alert"
        else:
            # Creation path: no alert ID provided.
            action = "create_alert"

        try:
            # Send the configuration to IBKR via a POST request.
            data = self.client.post(endpoint, json_data=payload)
            response = AlertResponse(**data)
            
            if response.success:
                msg_action = "created" if not existing_alert else "modified"
                self.logger.log_action(
                    action, 
                    message=f"Successfully {msg_action} alert '{request.alertName}'", 
                    account_id=account_id, 
                    alert_id=str(response.order_id),
                    details=payload
                )
            return response
        except Exception as e:
            self.logger.error(f"Failed to process alert {request.alertName}: {e}")
            raise

    def activate_deactivate_alert(self, account_id: str, alert_id: int, activate: bool) -> AlertResponse:
        """
        Toggle the active status of an existing alert.

        Args:
            account_id (str): Account ID.
            alert_id (int): Alert ID.
            activate (bool): True to activate, False to disable.

        Returns:
            AlertResponse: Success status of the request.
        """
        verb = "activating" if activate else "deactivating"
        self.logger.info(f"{verb.capitalize()} alert {alert_id}")
        
        endpoint = f"/iserver/account/{account_id}/alert/activate"
        payload = {
            "alertId": alert_id,
            "alertActive": 1 if activate else 0 # 1 for active, 0 for inactive
        }
        
        try:
            data = self.client.post(endpoint, json_data=payload)
            response = AlertResponse(**data)
            
            if response.success:
                self.logger.log_action(
                    "activate_deactivate", 
                    message=f"Successfully set alert {alert_id} activity to {activate}", 
                    account_id=account_id, 
                    alert_id=str(alert_id),
                    details=payload
                )
            return response
        except Exception as e:
            self.logger.error(f"Failed to set status for alert {alert_id}: {e}")
            raise

    def delete_alert(self, account_id: str, alert_id: int) -> AlertResponse:
        """
        Permanently delete an alert.

        Args:
            account_id (str): Account ID.
            alert_id (int): Alert ID (0 to delete all alerts).

        Returns:
            AlertResponse: Success status.
        """
        self.logger.info(f"Requesting deletion of alert {alert_id}")
        endpoint = f"/iserver/account/{account_id}/alert/{alert_id}"
        
        try:
            data = self.client.delete(endpoint)
            response = AlertResponse(**data)
            
            if response.success:
                self.logger.log_action(
                    "delete_alert", 
                    message=f"Deleted alert {alert_id} from account {account_id}", 
                    account_id=account_id, 
                    alert_id=str(alert_id)
                )
            return response
        except Exception as e:
            self.logger.error(f"Failed to delete alert {alert_id}: {e}")
            raise

    def get_mta_alert(self) -> Dict[str, Any]:
        """
        Retrieve the Mobile Trading Assistant (MTA) alert unique to the user.
        MTA alerts cannot be created or deleted, only retrieved or modified.

        Returns:
            Dict[str, Any]: Detailed configuration of the user's MTA alert.
        """
        self.logger.info("Fetching MTA alert information.")
        endpoint = "/iserver/account/mta"
        try:
            data = self.client.get(endpoint)
            self.logger.log_action("get_mta", message="Retrieved MTA alert.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch MTA alert: {e}")
            raise
