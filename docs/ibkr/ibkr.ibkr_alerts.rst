ibkr.ibkr\_alerts package
=========================

The ``ibkr_alerts`` tool allows you to manage server-side alerts and triggers directly through the IBKR API. These alerts can be based on price, volume, margin, or other financial conditions.

Features
--------

- **List & View**: Search for all active or disabled alerts on a specific account.
- **Dynamic Creation**: Create complex multi-condition alerts using JSON condition strings.
- **Lifecycle Management**: Activate, deactivate, or permanently delete alerts.
- **MTA Integration**: Retrieve Mobile Trading Assistant settings.

Usage
-----

.. code-block:: bash

    # List all alerts for a specific account
    python -m tools.ibkr.ibkr_alerts list --account DU12345

    # Create a new price-based alert
    python -m tools.ibkr.ibkr_alerts create --account DU12345 --name "AAPL > 200" --message "AAPL is above 200" --conditions '[{"type":"price","conid":265598,"operator":">","value":"200"}]'

    # Delete an alert by ID
    python -m tools.ibkr.ibkr_alerts delete --account DU12345 --alert_id 12345678

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``list``
     - **List all alerts.**
       
       * ``--account``: The target account ID (Required)
   * - ``get``
     - **Get alert details.**
       
       * ``--alert_id``: The unique ID of the alert (Required)
   * - ``create``
     - **Create or modify an alert.**
       
       * ``--account``: Target account ID (Required)
       * ``--name``: A descriptive name for the alert (Required)
       * ``--message``: The notification message text (Required)
       * ``--conditions``: JSON string of alert conditions (Required)
       * ``--repeatable``: 1 to allow repeating, 0 otherwise
       * ``--tif``: Time-in-Force (GTC or GTD)
       * ``--expire_time``: Required if tif is GTD (YYYYMMDD-HH:mm:ss)
       * ``--outside_rth``: 1 to trigger outside regular trading hours
       * ``--send_message``: 1 to send push/email notifications
       * ``--email``: Optional destination email address
   * - ``activate``
     - **Enable an alert.**
       
       * ``--account``: Primary account ID (Required)
       * ``--alert_id``: The alert ID to enable (Required)
   * - ``deactivate``
     - **Disable an alert.**
       
       * ``--account``: Primary account ID (Required)
       * ``--alert_id``: The alert ID to disable (Required)
   * - ``delete``
     - **Remove an alert.**
       
       * ``--account``: Primary account ID (Required)
       * ``--alert_id``: The alert ID to delete (Required)
   * - ``get-mta``
     - **Fetch Mobile Trading Assistant info.**

Submodules
----------

ibkr.ibkr\_alerts.cli module
----------------------------

.. automodule:: ibkr.ibkr_alerts.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_alerts.core module
-----------------------------

.. automodule:: ibkr.ibkr_alerts.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_alerts
   :members:
   :show-inheritance:
   :undoc-members:
