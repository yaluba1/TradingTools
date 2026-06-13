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

    # 1. List portfolio accounts
    python -m tools.ibkr.ibkr_portfolio accounts

    # 2. List portfolio sub-accounts
    python -m tools.ibkr.ibkr_portfolio subaccounts

    # 3. Get account metadata/attributes
    python -m tools.ibkr.ibkr_portfolio meta --account U1234567

    # 4. Get portfolio summary characteristics for an account
    python -m tools.ibkr.ibkr_portfolio summary --account U1234567

    # 5. View account ledger (balances across currencies)
    python -m tools.ibkr.ibkr_portfolio ledger --account U1234567

    # 6. Get positions for a specific account (all positions)
    python -m tools.ibkr.ibkr_portfolio positions --account U1234567

    # 7. Get positions for a specific account with pagination (optional page ID)
    python -m tools.ibkr.ibkr_portfolio positions --account U1234567 --page 0

    # 8. Get near-real-time (uncached) positions for an account (bypasses gateway cache)
    python -m tools.ibkr.ibkr_portfolio positions-nocache --account U1234567

    # 9. Get near-real-time positions sorted by market price in descending order
    python -m tools.ibkr.ibkr_portfolio positions-nocache --account U1234567 --sort mktPrice --direction d

    # 10. Get details for a specific contract position in a specific account
    python -m tools.ibkr.ibkr_portfolio position --account U1234567 --conid 265598

    # 11. Get positions across all accounts for a specific contract ID
    python -m tools.ibkr.ibkr_portfolio positions-conid --conid 265598

    # 12. Invalidate portfolio positions cache
    python -m tools.ibkr.ibkr_portfolio invalidate --account U1234567

    # 13. Get global account asset allocation breakdown (Account Allocations)
    python -m tools.ibkr.ibkr_portfolio allocation

    # 14. Get account asset allocation breakdown for a specific account (Account Allocations)
    python -m tools.ibkr.ibkr_portfolio allocation --account U1234567

    # 15. Get consolidated PA portfolio allocation across accounts (Portfolio Allocation)
    python -m tools.ibkr.ibkr_portfolio pa-allocation --accounts U1234567 --type ASSET_CLASS

    # 16. Get consolidated PA portfolio allocation with optional filters
    python -m tools.ibkr.ibkr_portfolio pa-allocation --accounts U1234567 U7654321 --type ALL --currency USD --date 20260613 --model model1

    # 17. Get performance data (TWR/NAV) for a list of accounts
    python -m tools.ibkr.ibkr_portfolio performance --accounts U1234567 U7654321 --period 1M

    # 18. Get performance data (TWR/NAV) for all periods for a list of accounts
    python -m tools.ibkr.ibkr_portfolio performance-all --accounts U1234567 U7654321

    # 19. List historical transactions
    python -m tools.ibkr.ibkr_portfolio transactions --accounts U1234567 --conids 265598 --currency USD --days 30

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``accounts``
     - **List portfolio accounts.** Retrieves all accounts associated with the session.
   * - ``subaccounts``
     - **List sub-accounts.** Retrieves sub-accounts for tiered configurations (FAs, Brokers).
   * - ``meta``
     - **Account Metadata.** Get attributes and configuration metadata for an account.
       
       * ``--account``: Account ID (Required)
   * - ``summary``
     - **Portfolio Summary.** Get portfolio summary characteristics for an account.
       
       * ``--account``: Account ID (Required)
   * - ``ledger``
     - **Account Ledger.** View balances, cash, and PnL per currency.
       
       * ``--account``: Account ID (Required)
   * - ``positions``
     - **View Positions (Cached).** List holdings in an account.
       
       * ``--account``: Account ID (Required)
       * ``--page``: Optional page number for pagination
   * - ``positions-nocache``
     - **View Positions (Near-Real-Time).** List holdings bypassing the gateway cache.
       Unlike the cached ``positions`` command, this endpoint fetches all positions in one request and supports sorting/filtering on the backend.
       
       * ``--account``: Account ID (Required)
       * ``--model``: Optional model portfolio code
       * ``--sort``: Optional column to sort by (e.g. ``position``, ``mktPrice``)
       * ``--direction``: Optional sort order direction: ``a`` (ascending) or ``d`` (descending)
   * - ``position``
     - **View Single Position.** Get details of a position for a specific contract ID.
       
       * ``--account``: Account ID (Required)
       * ``--conid``: Contract ID (Required)
   * - ``positions-conid``
     - **View Positions for Contract.** Get positions across all accounts for a specific contract ID.
       
       * ``--conid``: Contract ID (Required)
   * - ``invalidate``
     - **Invalidate Cache.** Force the gateway to refresh positions data from the backend.
        
        * ``--account``: Account ID (Required)
   * - ``allocation``
     - **Account Allocations (Asset Allocation).** Get asset class, sector, and grouping allocation.
       
       * ``--account``: Optional Account ID (Global if omitted)
   * - ``pa-allocation``
     - **Portfolio Allocation (PA Allocation).** Get consolidated allocation across accounts from Portfolio Analyst.
       
       * ``--accounts``: List of Account IDs (Required)
       * ``--type``: Allocation category: ALL, ASSET_CLASS, COUNTRY, FINANCIAL_INSTRUMENT, REGION, SECTOR (Required)
       * ``--currency``: Optional base currency filter (e.g., USD, EUR)
       * ``--date``: Optional reporting date (e.g., 20260613)
       * ``--model``: Optional model identifier
   * - ``performance``
     - **PA Performance.** Use Portfolio Analyst to get performance metrics.
       
       * ``--accounts``: List of Account IDs (Required)
       * ``--period``: Period: 1D, 7D, MTD, 1M, 3M, 6M, 12M, YTD. (Default: 12M)
   * - ``performance-all``
     - **PA Performance (All Periods).** Get performance metrics across all periods from Portfolio Analyst.
       
       * ``--accounts``: List of Account IDs (Required)
   * - ``pa-summary``
     - **PA Summary.** Get analysis summary for a list of accounts.
       
       * ``--accounts``: List of Account IDs (Required)
   * - ``transactions``
     - **View Transactions.** Historical transactions from Portfolio Analyst.
        
        * ``--accounts``: List of Account IDs (Required)
        * ``--conids``: List of Contract IDs (Required)
        * ``--currency``: Currency code (Required)
        * ``--days``: Lookback period in days (Optional, default: 90)

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
