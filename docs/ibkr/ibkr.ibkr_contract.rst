ibkr.ibkr\_contract package
===========================

The ``ibkr_contract`` tool is used to search for financial instruments, retrieve detailed contract specifications, trading rules, currency pairings, exchange rates, available algorithms, and option derivatives.

Features
--------

- **Contract Search**: Find contracts using ticker symbols, filters, and fuzzy matching.
- **Detailed Rules**: Retrieve trading rules, instrument details, and ConIDs.
- **Option Strikes**: Fetch available strike prices and expiration months for options.
- **Trading Schedule**: View the trading hours and sessions for an instrument by ConID or symbol.
- **Trading Algos**: Fetch supported execution algorithms for specific contracts.
- **Currency Details**: Query exchange rates and active currency trading pairs.
- **Exchanges & Futures**: List stock ConIDs by exchange, resolve futures chains, and batch query security definitions.
- **Event Contracts (Forecast)**: List categories, query outcome details, underlying markets, rule parameters, and weekly trading schedules.

Usage
-----

.. code-block:: bash

    # Search for a contract by symbol (with asset class filter)
    python -m tools.ibkr.ibkr_contract search --symbol AAPL --sectype STK --name

    # Get detailed contract info
    python -m tools.ibkr.ibkr_contract details --conid 265598 --exchange SMART

    # Get option strikes for an underlying
    python -m tools.ibkr.ibkr_contract strikes --conid 265598 --sectype OPT --month OCT24

    # Get trading schedule by ConID
    python -m tools.ibkr.ibkr_contract schedule --conid 265598

    # Get trading schedule by Symbol
    python -m tools.ibkr.ibkr_contract schedule-by-symbol --symbol AAPL --sectype STK

    # Get contract trading rules
    python -m tools.ibkr.ibkr_contract rules --conid 265598 --is-buy

    # Get execution algos for a contract
    python -m tools.ibkr.ibkr_contract algos --conid 265598 --add-description 1 --add-params 1

    # Get detailed instrument info
    python -m tools.ibkr.ibkr_contract info --conid 265598

    # Get combined instrument info and rules
    python -m tools.ibkr.ibkr_contract info-and-rules --conid 265598

    # Get FX currency pairs
    python -m tools.ibkr.ibkr_contract currency-pairs --currency USD

    # Get exchange rate
    python -m tools.ibkr.ibkr_contract exchange-rate --source USD --target EUR

    # Get bond filters
    python -m tools.ibkr.ibkr_contract bond-filters --issuer-id US-TREASURY

    # List all ConIDs on an exchange
    python -m tools.ibkr.ibkr_contract all-conids --exchange NASDAQ

    # Search futures by underlying symbol
    python -m tools.ibkr.ibkr_contract futures --symbols ES,NQ

    # Fetch security definitions in batch
    python -m tools.ibkr.ibkr_contract secdef --conids 265598,12345

    # Search stocks by symbol list
    python -m tools.ibkr.ibkr_contract stocks --symbols AAPL,IBM

    # List forecast categories and underlying markets
    python -m tools.ibkr.ibkr_contract forecast-categories

    # Get detailed attributes of a specific forecast outcome contract
    python -m tools.ibkr.ibkr_contract forecast-details --conid 849540484

    # Query all outcomes for an underlying market
    python -m tools.ibkr.ibkr_contract forecast-market --underlying-conid 848765505

    # Retrieve rules and price increments for a forecast contract
    python -m tools.ibkr.ibkr_contract forecast-rules --conid 849540484

    # View trading schedules for a forecast contract
    python -m tools.ibkr.ibkr_contract forecast-schedules --conid 849540484

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
       * ``--sectype``: Asset class filter (e.g. STK, OPT)
       * ``--name``: Boolean flag to search in company name
       * ``--referrer``: Referrer system source
   * - ``details``
     - **Get contract details.**
       
       * ``--conid``: The contract ID (Required)
       * ``--sectype``: Security type
       * ``--type``: Security type alias (backwards-compatible)
       * ``--month``: Expiration month YYYYMM
       * ``--exchange``: Exchange name
       * ``--strike``: Option strike price
       * ``--right``: C or P option right
   * - ``strikes``
     - **Get option strikes.**
       
       * ``--conid``: Underlying contract ID (Required)
       * ``--sectype``: Security type (Required)
       * ``--type``: Security type alias (backwards-compatible)
       * ``--month``: Expiration month (Required)
       * ``--exchange``: Target exchange, defaults to 'SMART'
   * - ``schedule``
     - **Get trading schedule by ConID.**
       
       * ``--conid``: The contract ID (Required)
       * ``--exchange``: Target exchange name
   * - ``schedule-by-symbol``
     - **Get trading schedule by Symbol.**
       
       * ``--symbol``: Ticker symbol (Required)
       * ``--sectype``: Security type (Required)
       * ``--exchange``: Target exchange name
   * - ``rules``
     - **Get contract trading rules.**
       
       * ``--conid``: The contract ID (Required)
       * ``--is-buy``: Set to query buy-side rules
       * ``--no-buy``: Set to query sell-side rules
       * ``--exchange``: Exchange name
   * - ``algos``
     - **Get available trading algos.**
       
       * ``--conid``: The contract ID (Required)
       * ``--add-description``: 1 to add descriptions
       * ``--add-params``: 1 to add parameters
       * ``--algos``: Semicolon-separated list of algos
   * - ``info``
     - **Get general instrument info.**
       
       * ``--conid``: The contract ID (Required)
   * - ``info-and-rules``
     - **Get combined contract info and rules.**
       
       * ``--conid``: The contract ID (Required)
   * - ``currency-pairs``
     - **Get currency pairs.**
       
       * ``--currency``: Target currency (Required)
   * - ``exchange-rate``
     - **Get currency exchange rates.**
       
       * ``--source``: Base currency (Required)
       * ``--target``: Quote currency (Required)
   * - ``bond-filters``
     - **Get bond filters.**
       
       * ``--issuer-id``: Issuer ID (Required)
       * ``--symbol``: Defaults to BOND
   * - ``all-conids``
     - **Get all Stock ConIDs on exchange.**
       
       * ``--exchange``: Target exchange name (Required)
   * - ``futures``
     - **Search futures by symbol.**
       
       * ``--symbols``: Comma-separated symbols (Required)
   * - ``secdef``
     - **Fetch security definitions by ConIDs.**
       
       * ``--conids``: Comma-separated ConIDs (Required)
   * - ``stocks``
     - **Search stocks by symbols.**
       
       * ``--symbols``: Comma-separated stock symbols (Required)
   * - ``forecast-categories``
     - **List forecast categories.**
       
       Lists all Event Contract Forecast categories, subcategories, and underlying markets/ConIDs.
   * - ``forecast-details``
     - **Get detailed forecast contract outcomes.**
       
       * ``--conid``: The contract outcome ID (Required)
   * - ``forecast-market``
     - **Get contracts under underlying market.**
       
       * ``--underlying-conid``: The underlying market ConID (Required)
   * - ``forecast-rules``
     - **Get rules for a forecast contract.**
       
       * ``--conid``: The contract outcome ID (Required)
   * - ``forecast-schedules``
     - **Get weekly schedules for a forecast contract.**
       
       * ``--conid``: The contract outcome ID (Required)

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
