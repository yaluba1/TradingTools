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

    # 1. Place a limit order with auto-confirmation
    python -m tools.ibkr.ibkr_orders place --account DU123 --conid 265598 --side BUY --type LMT --qty 10 --price 150.0 --auto-confirm

    # 2. Modify an existing open order with auto-confirmation
    python -m tools.ibkr.ibkr_orders modify --account DU123 --id 761318694 --conid 265598 --side BUY --type LMT --qty 15 --price 149.0 --auto-confirm

    # 3. Cancel a live order
    python -m tools.ibkr.ibkr_orders cancel --account DU123 --cid cust-123

    # 4. Preview the margin and commission impact of an order (What-If)
    python -m tools.ibkr.ibkr_orders preview --account DU123 --conid 265598 --side BUY --type LMT --qty 10 --price 150.0

    # 5. List live filled orders in a table format
    python -m tools.ibkr.ibkr_orders list --account DU123 --status Filled --table

    # 6. Get detailed status of a specific order
    python -m tools.ibkr.ibkr_orders status --id 761318694

    # 7. Fetch active/pending system questions from IBKR
    python -m tools.ibkr.ibkr_orders questions --table

    # 8. Reply to an active question/warning
    python -m tools.ibkr.ibkr_orders reply --id q-1 --confirm yes

    # 9. Suppress specific order warning/reply messages
    python -m tools.ibkr.ibkr_orders suppress --ids o163 o10082

    # 10. Reset all order warning suppressions
    python -m tools.ibkr.ibkr_orders suppress-reset

    # 11. Synchronize the local database with the live IBKR orders state
    python -m tools.ibkr.ibkr_orders sync --account DU123

    # 12. Run a continuous background synchronization loop
    python -m tools.ibkr.ibkr_orders background-sync --interval 60 --account DU123

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
       * ``--id``: Order ID to modify (server order ID or customer order ID) (Required)
       * ``--cid``: Optional new customer order ID (cId)
       * ``--conid``: Contract ID (Required)
       * ``--side``: BUY or SELL (Default BUY)
       * ``--type``: New order type
       * ``--qty``: New quantity
       * ``--price``: New limit price
       * ``--aux``: New stop price
       * ``--tif``: New Time-in-Force
       * ``--auto-confirm``: Automatically accept price/margin warnings
   * - ``cancel``
     - **Cancel a live order.**
       
       * ``--account``: Primary account ID (Required)
       * ``--cid``: Customer ID to cancel (Required)
   * - ``list``
     - **Monitor live orders.**
       
       * ``--account``: Filter by account (applied locally, compatible with modern ``acct`` / ``acctId`` responses)
       * ``--status``: Filter by status (e.g., Filled, Submitted). If ``--filters`` is omitted, the API filter is automatically derived from this value to ensure the gateway returns matching records.
       * ``--filters``: Optional query status filter (active, filled, cancelled, inactive). Automatically case-normalized (e.g., ``submitted`` -> ``Submitted``) to satisfy case-sensitive IBKR gateway constraints.
       * ``--force``: Force refresh orders from the gateway
       * ``--table``: Output as formatted text instead of JSON
   * - ``preview``
     - **Preview order effects (What-If).**
       
       * ``--account``: Primary account ID (Required)
       * ``--conid``: IBKR Contract ID (Required)
       * ``--side``: BUY or SELL (Required)
       * ``--type``: LMT, MKT, STP (Required)
       * ``--qty``: Quantity (Required)
       * ``--price``: Limit price
       * ``--aux``: Stop price
       * ``--tif``: Time-In-Force
       * ``--cid``: Custom order ID
   * - ``suppress``
     - **Suppress warning messages.**
       
       * ``--ids``: List of message/warning IDs to suppress (Required)
   * - ``suppress-reset``
     - **Reset warning suppressions.**
       
       Clears all active session-based warning suppressions.
   * - ``questions``
     - **Retrieve system prompts.**
       
       * ``--table``: Output as formatted text
   * - ``reply``
     - **Respond to a specific prompt.**
       
       * ``--id``: The reply ID from the question (Required)
       * ``--confirm``: yes or no (Required)

Order Reply Warning Message IDs
-------------------------------

When placing orders, the IBKR Client Portal Web API may return warnings or confirmation prompts requiring a response. You can suppress these specific warnings for your session using the ``suppress`` command.

Below is a reference of common IBKR warning message IDs and their descriptions:

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Message ID
     - Description / Warning Type
   * - ``o163``
     - **Price percentage limit constraint** (e.g., price exceeds the 3% price variance check).
   * - ``o354``
     - **No market data warning** (order submitted without subscribing to or receiving real-time market data).
   * - ``o382``
     - **Tick size limit exceeded** (the order price value exceeds or violates the minimum tick size increment).
   * - ``o383``
     - **Size limit exceeded** (the quantity/size of the order exceeds predefined system or user-defined limits).
   * - ``o403``
     - **Immediate trigger/fill warning** (the limit price suggests the order is highly likely to trigger and fill immediately).
   * - ``o451``
     - **Total value limit exceeded** (the estimated total value of the order exceeds the account's total value limit).
   * - ``o2136``
     - **Mixed allocation warning** (warning triggered for orders with multiple or mixed allocation templates).
   * - ``o2137``
     - **Cross-side order warning** (warning when an order conflicts with/crosses another order from the same client).
   * - ``o2165``
     - **Fractional trading outside regular hours** (warns that the instrument does not support trading fractional shares outside of regular trading hours).
   * - ``o10082``
     - **Called Bond warning** (warning that the bond has been called by the issuer before maturity).
   * - ``o10138``
     - **Size modification limit exceeded** (modifying the order size exceeds the maximum size adjustment allowed).
   * - ``o10151``
     - **Market Order risks** (warning explaining the price execution risks associated with submitting Market Orders).
   * - ``o10152``
     - **Stop Order risks** (warning advising on the execution and slippage risks associated with Stop Orders once they become active).
   * - ``o10153``
     - **Mandatory Cap Price confirmation** (requires confirmation of the mandatory cap price protection limit).
   * - ``o10164``
     - **Cash Quantity details note** (notes that cash quantity-based order sizes are handled on a best-efforts basis).
   * - ``o10223``
     - **Cash Quantity non-guaranteed warning** (confirmation that filling cash quantity orders is not guaranteed to exact decimal values).
   * - ``o10288``
     - **Crypto Market Order risks** (specific warning regarding high volatility and risk when using Market Orders for cryptocurrency trading).
   * - ``o10331``
     - **Stop order submission warning** (general reminder warning to be aware of the different stop order types and their specific behaviors).
   * - ``o10332``
     - **OSL Digital Securities LTD warning** (specific regulatory/disclosure warning for Crypto trades routed through OSL).
   * - ``o10333``
     - **Option Exercise At-The-Money warning** (warning triggered during exercise requests for options that are at or near the money).
   * - ``o10334``
     - **Omnibus account routing** (warns that the order will be placed into the omnibus account instead of the global account).
   * - ``o10335``
     - **Rapid Entry window message** (internal status/warning used by the Rapid Entry order entry interface).
   * - ``o10336``
     - **Limited liquidity risk** (warns that the security is illiquid and may be difficult to buy or sell at a fair market price).
   * - ``p6``
     - **Multiple accounts distribution** (acknowledges that the order will be split or distributed across multiple accounts).
   * - ``p12``
     - **Limit price too far from reference price** (warns that the order may be rejected by the exchange or clearinghouse because the limit price is too far out of line).

For official documentation on warning handling and suppression, see the `IBKR Campus Web API Documentation <https://www.interactivebrokers.com/campus/ibkr-api-page/web-api>`_ and the `IBKR Campus Web API Reference <https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-ref/>`_.

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
