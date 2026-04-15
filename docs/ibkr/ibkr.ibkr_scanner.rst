ibkr.ibkr\_scanner package
==========================

The ``ibkr_scanner`` tool provides a powerful interface to the Interactive Brokers market scanner. This tool uses the standard ``/iserver/scanner`` endpoints to perform real-time market discovery based on asset classes, scan types, and exchange locations.

Features
--------

- **Parameter Discovery**: Retrieve the latest available scanner types, instrument codes, exchange locations, and filter definitions.
- **Customized Scans**: Execute scans with specific instrument types (e.g., ``STK``, ``FUT``), scan types (e.g., ``MOST_ACTIVE``, ``TOP_GAINERS``), and locations (e.g., ``STK.US.MAJOR``).
- **Simplified Filtering**: Easily apply common filters like price range and volume via dedicated CLI arguments.
- **Detailed Logging**: Support for debug-level logging to trace all API interactions and response parsing.

Usage
-----

.. code-block:: bash

    # View available scanner parameters (Disclaimer: 15-minute rate limit)
    python -m tools.ibkr.ibkr_scanner params

    # Run a simple scan for most active US stocks
    python -m tools.ibkr.ibkr_scanner run --instrument STK --type MOST_ACTIVE --location STK.US.MAJOR

    # Run a scan with price and volume filters
    python -m tools.ibkr.ibkr_scanner run --instrument STK --type TOP_GAINERS --location STK.US.MAJOR --price-min 10 --price-max 100 --volume-min 1000000

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``params``
     - **Retrieve Scanner Parameters.** Fetches the XML/JSON parameter tree which defines allowed values for all other commands. **Note: IBKR limits this endpoint to 1 request every 15 minutes.**
   * - ``run``
     - **Execute a Market Scan.**
       
       * ``--instrument``: The asset class to scan. Common values: ``STK`` (Stocks), ``FUT`` (Futures), ``OPT`` (Options), ``IND`` (Indices).
       * ``--type``: The specific scan criteria. Common values: ``MOST_ACTIVE``, ``HOT_BY_VOLUME``, ``TOP_GAINERS``, ``TOP_LOSERS``, ``HOT_BY_PRICE``.
       * ``--location``: The exchange or geographical region. Common values: ``STK.US``, ``STK.US.MAJOR``, ``FUT.US``.
       * ``--price-min``: Filter results with a price strictly above this value.
       * ``--price-max``: Filter results with a price strictly below this value.
       * ``--volume-min``: Filter results with a daily volume strictly above this value.

Rate Limits
-----------

IBKR enforces strict rate limits for the scanner:
- **/iserver/scanner/params**: 1 request every 15 minutes.
- **/iserver/scanner/run**: Regular API pacing limits apply (typically 10 requests per second via the Gateway).

Submodules
----------

ibkr.ibkr\_scanner.cli module
-----------------------------

.. automodule:: ibkr.ibkr_scanner.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_scanner.core module
------------------------------

.. automodule:: ibkr.ibkr_scanner.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_scanner
   :members:
   :show-inheritance:
   :undoc-members:
