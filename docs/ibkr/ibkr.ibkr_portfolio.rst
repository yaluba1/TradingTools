ibkr.ibkr\_portfolio package
============================

The ``ibkr_portfolio`` tool provides a comprehensive interface for managing and analyzing your Interactive Brokers portfolio. It merges functionalities from the "Portfolio" and "Portfolio Analyst" (PA) API families, allowing for real-time holdings tracking and historical performance analysis.

Features
--------

- **Account Management**: List and inspect brokerage accounts and sub-accounts.
- **Holdings Tracking**: View real-time positions, summaries, and ledgers (balances).
- **Allocation Analysis**: View portfolio distribution by asset class, sector, or group.
- **Performance Analysis**: Retrieve historical performance benchmarks, NAV, and TWR from Portfolio Analyst.
- **Transaction History**: Inspect historical trades and transactions across multiple accounts.

Usage
-----

.. code-block:: bash

    # List portfolio accounts
    python -m tools.ibkr.ibkr_portfolio accounts

    # Get positions for a specific account
    python -m tools.ibkr.ibkr_portfolio positions --account U1234567

    # View account ledger (balances across currencies)
    python -m tools.ibkr.ibkr_portfolio ledger --account U1234567

    # Get performance data (TWR/NAV) for a list of accounts
    python -m tools.ibkr.ibkr_portfolio performance --accounts U1234567 U7654321 --freq M

    # List historical transactions
    python -m tools.ibkr.ibkr_portfolio transactions --accounts U1234567 --days 30

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``accounts``
     - **List portfolio accounts.** Retrieves all accounts associated with the session.
   * - ``summary``
     - **Portfolio Summary.**
       
       * ``--account``: Account ID (Required)
   * - ``ledger``
     - **Account Ledger.** View balances, cash, and PnL per currency.
       
       * ``--account``: Account ID (Required)
   * - ``positions``
     - **View Positions.** List holdings in an account.
       
       * ``--account``: Account ID (Required)
       * ``--page``: Page number for pagination (Default: 0)
   * - ``invalidate``
     - **Invalidate Cache.** Force the gateway to refresh positions data from the backend.
   * - ``allocation``
     - **View Allocation.**
       
       * ``--account``: Optional Account ID (Global if omitted)
   * - ``performance``
     - **PA Performance.** Use Portfolio Analyst to get performance metrics.
       
       * ``--accounts``: List of Account IDs (Required)
       * ``--freq``: Frequency: D (Daily), M (Monthly), Q (Quarterly), Y (Yearly). (Default: D)
   * - ``pa-summary``
     - **PA Summary.** Get analysis summary for a list of accounts.
       
       * ``--accounts``: List of Account IDs (Required)
   * - ``transactions``
     - **View Transactions.** Historical transactions from Portfolio Analyst.
       
       * ``--accounts``: List of Account IDs (Required)
       * ``--conid``: Optional Contract ID filter
       * ``--days``: Optional lookback period in days

Submodules
----------

ibkr.ibkr\_portfolio.cli module
-------------------------------

.. automodule:: ibkr.ibkr_portfolio.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_portfolio.core module
--------------------------------

.. automodule:: ibkr.ibkr_portfolio.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_portfolio
   :members:
   :show-inheritance:
   :undoc-members:
