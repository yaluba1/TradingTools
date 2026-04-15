ibkr.ibkr\_accounts package
===========================

The ``ibkr_accounts`` tool provides access to account-level information, including balances, PnL tracking, and ownership details.

Features
--------

- **Account Listing**: View all accessible brokerage accounts and the current session context.
- **PnL Tracking**: Retrieve real-time Profit and Loss data for the session.
- **Ownership Info**: Access detailed signature and ownership information for specific accounts.

Usage
-----

.. code-block:: bash

    # List all accessible accounts
    python -m tools.ibkr.ibkr_accounts list

    # Retrieve current session PnL
    python -m tools.ibkr.ibkr_accounts pnl

    # Get ownership and signature details for an account
    python -m tools.ibkr.ibkr_accounts ownership --account DU12345

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``list``
     - **List all accessible accounts.**
       Returns a list of account identifiers and session details.
   * - ``pnl``
     - **Retrieve PnL data.**
       Fetches current session Profit and Loss across partitions.
   * - ``ownership``
     - **Retrieve ownership info.**
       
       * ``--account``: The target account ID (Required)

Submodules
----------

ibkr.ibkr\_accounts.cli module
------------------------------

.. automodule:: ibkr.ibkr_accounts.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_accounts.core module
-------------------------------

.. automodule:: ibkr.ibkr_accounts.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_accounts
   :members:
   :show-inheritance:
   :undoc-members:
