ibkr.ibkr\_contract package
==========================

The ``ibkr_contract`` tool is used to search for financial instruments and retrieve detailed contract specifications, trading rules, and option derivatives.

Features
--------

- **Contract Search**: Find contracts using ticker symbols and fuzzy matching.
- **Detailed Rules**: Retrieve trading rules, instrument details, and ConIDs.
- **Option Strikes**: Fetch available strike prices and expiration months for options.
- **Trading Schedule**: View the trading hours and sessions for an instrument.

Usage
-----

.. code-block:: bash

    # Search for a contract by symbol
    python -m tools.ibkr.ibkr_contract search --symbol AAPL

    # Get detailed rules and info for a ConID
    python -m tools.ibkr.ibkr_contract details --conid 265598

    # Get option strikes for an underlying
    python -m tools.ibkr.ibkr_contract strikes --conid 265598 --type OPT --month OCT24

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``search``
     - **Search for contracts.**
       
       * ``--symbol``: Ticker symbol to search for (Required)
   * - ``details``
     - **Get contract details.**
       
       * ``--conid``: The contract ID (Required)
       * ``--type``: Security type, defaults to 'STK'
   * - ``strikes``
     - **Get option strikes.**
       
       * ``--conid``: Underlying contract ID (Required)
       * ``--type``: Security type, e.g., 'OPT' (Required)
       * ``--month``: Expiration month (Required)
       * ``--exchange``: Target exchange, defaults to 'SMART'
   * - ``schedule``
     - **Get trading schedule.**
       
       * ``--conid``: The contract ID (Required)

Submodules
----------

ibkr.ibkr\_contract.cli module
------------------------------

.. automodule:: ibkr.ibkr_contract.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_contract.core module
-------------------------------

.. automodule:: ibkr.ibkr_contract.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_contract
   :members:
   :show-inheritance:
   :undoc-members:
