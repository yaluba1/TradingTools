ibkr.ibkr\_orders package
==========================

The ``ibkr_orders`` tool provides a comprehensive interface for managing and tracking orders with Interactive Brokers. It combines order execution (placement, modification, cancellation) with session-based order monitoring.

Features
--------

- **Order Placement**: Place single or multiple orders with automatic handling of IBKR warnings via ``--auto-confirm``.
- **Order Monitoring**: List live orders with status filtering (Working, Filled, Cancelled).
- **System Questions**: Retrieve and respond to pending IBKR prompts or warnings.
- **Database Persistence**: Every execution and status change is logged in the local MariaDB database.

Usage
-----

.. code-block:: bash

    # Place a limit order with auto-confirmation
    python -m tools.ibkr.ibkr_orders place --account DU123 --conid 265598 --side BUY --type LMT --qty 10 --price 150.0 --auto-confirm

    # List live filled orders in a table format
    python -m tools.ibkr.ibkr_orders list --account DU123 --status Filled --table

    # Fetch pending questions
    python -m tools.ibkr.ibkr_orders questions --table

    # Sync orders with the database
    python -m tools.ibkr.ibkr_orders sync --account DU123

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``place``
     - **Place a new order.**
       
       * ``--account``: Primary account ID (Required)
       * ``--conid``: IBKR Contract ID (Required)
       * ``--side``: BUY or SELL (Required)
       * ``--type``: LMT, MKT, STP (Required)
       * ``--qty``: Quantity to trade (Required)
       * ``--price``: Limit price for LMT orders
       * ``--aux``: Stop price for STP orders
       * ``--tif``: Time-In-Force (DAY, GTC)
       * ``--auto-confirm``: Automatically accept price/margin warnings
       * ``--cid``: Optional custom order ID
   * - ``modify``
     - **Modify an existing order.**
       
       * ``--account``: Primary account ID (Required)
       * ``--cid``: Customer ID of the order to modify (Required)
       * ``--conid``: Contract ID (Required)
       * ``--type``: New order type
       * ``--qty``: New quantity
       * ``--price``: New limit price
       * ``--aux``: New stop price
   * - ``cancel``
     - **Cancel a live order.**
       
       * ``--account``: Primary account ID (Required)
       * ``--cid``: Customer ID to cancel (Required)
   * - ``list``
     - **Monitor live orders.**
       
       * ``--account``: Filter by account
       * ``--status``: Filter by status (e.g., Filled, Submitted)
       * ``--table``: Output as formatted text instead of JSON
   * - ``questions``
     - **Retrieve system prompts.**
       
       * ``--table``: Output as formatted text
   * - ``reply``
     - **Respond to a specific prompt.**
       
       * ``--id``: The reply ID from the question (Required)
       * ``--confirm``: yes or no (Required)

Submodules
----------

ibkr.ibkr\_orders.cli module
-----------------------------

.. automodule:: ibkr.ibkr_orders.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_orders.core module
------------------------------

.. automodule:: ibkr.ibkr_orders.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_orders
   :members:
   :show-inheritance:
   :undoc-members:
