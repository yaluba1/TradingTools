ibkr.ibkr\_marketdata package
=============================

The ``ibkr_marketdata`` tool provides a comprehensive interface for retrieving market data from Interactive Brokers, specifically supporting historical OHLCV bar data queries.

Features
--------

- **Historical OHLCV**: Retrieve historical open, high, low, close, and volume candles.
- **Flexible Bar Sizes**: Query data with fine granularity from 1 minute up to daily or weekly bars.
- **Durations**: Retrieve historical ranges spanning from 1 day up to multiple years.
- **Outside RTH**: Option to include pre-market and after-hours trading session data.
- **Data Customization**: Supports multiple bar pricing fields including Last, Bid, Ask, Midpoint, and Inventory.
- **Automatic Validation**: Validates the payload using robust Pydantic schemas.

Usage
-----

.. code-block:: bash

    # Retrieve 2 days of 1 hour bars for Apple Inc. (ConID: 265598)
    python -m tools.ibkr.ibkr_marketdata history --conid 265598 --period 2d --bar 1h

    # Retrieve 1 week of daily bars including pre-market/after-hours data
    python -m tools.ibkr.ibkr_marketdata history --conid 265598 --period 1w --bar 1d --outside-rth

    # Retrieve midpoint candles since a specific start time
    python -m tools.ibkr.ibkr_marketdata history --conid 265598 --period 1d --bar 5min --bar-type midprice --start-time 20260520-09:30:00

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``history``
     - **Get Historical OHLC Bar Data.**
       
       Retrieves OHLCV bars for a specified contract ID backwards from a specific duration.
       
       * ``--conid``: The unique contract ID of the instrument. (Required, Integer)
       * ``--period``: The total duration of data to retrieve (e.g. ``1d``, ``1w``, ``1m``, ``1y``). (Required)
       * ``--bar``: The bar size / interval (e.g. ``1min``, ``5min``, ``1h``, ``1d``). (Required)
       * ``--outside-rth``: Flag to include data from outside regular trading hours. (Optional)
       * ``--bar-type``: Pricing data source (e.g. ``last``, ``midprice``, ``bid``, ``ask``, ``inventory``). (Optional)
       * ``--start-time``: Retrieve data starting from YYYYMMDD-hh:mm:ss. (Optional)

Implementation Details
----------------------

The tool enforces compliance with IBKR Gateway's strict 10 requests per second rate limiting. Historical market data calls are pacing-aware and logged to a central database table (``ibkr_logs``) to capture performance and usage metrics.

Submodules
----------

ibkr.ibkr\_marketdata.cli module
--------------------------------

.. automodule:: ibkr.ibkr_marketdata.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_marketdata.core module
---------------------------------

.. automodule:: ibkr.ibkr_marketdata.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_marketdata
   :members:
   :show-inheritance:
   :undoc-members:
