ibkr.ibkr\_accounts package
===========================

The ``ibkr_accounts`` tool provides access to account-level information, including balances, PnL tracking, and ownership details.

Features
--------

- **Account Listing**: View all accessible brokerage accounts and the current session context.
- **PnL Tracking**: Retrieve real-time Profit and Loss data for the session.
- **Ownership Info**: Access comprehensive ownership details for specific accounts, including user roles, entity information, and applicant signatures.

Usage
-----

.. code-block:: bash

    # List all accessible accounts
    python -m tools.ibkr.ibkr_accounts list

    # Retrieve current session PnL
    python -m tools.ibkr.ibkr_accounts pnl

    # Get ownership and signature details for an account
    python -m tools.ibkr.ibkr_accounts ownership --account DU12345

    # Search for dynamic accounts
    python -m tools.ibkr.ibkr_accounts search --pattern "U123*"

    # Retrieve account summary
    python -m tools.ibkr.ibkr_accounts summary --account DU12345

    # Retrieve available funds summary
    python -m tools.ibkr.ibkr_accounts funds --account DU12345

    # Retrieve account balances summary
    python -m tools.ibkr.ibkr_accounts balances --account DU12345

    # Retrieve account margin usage summary
    python -m tools.ibkr.ibkr_accounts margins --account DU12345

    # Retrieve account market value summary
    python -m tools.ibkr.ibkr_accounts market_value --account DU12345

    # Set active dynamic account
    python -m tools.ibkr.ibkr_accounts set_active --account DU12345

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``balances``
     - **Retrieve a comprehensive summary of account balances.**
       Returns a comprehensive object including total balances summary and CFD specific details.

       * ``--account``: The target account ID (Required)

   * - ``margins``
     - **Retrieve a comprehensive summary of account margin usage.**
       Returns a comprehensive object including total margin summary and CFD specific details.

       * ``--account``: The target account ID (Required)

   * - ``market_value``
     - **Retrieve a comprehensive summary of account market value by currency.**
       Returns a dictionary where keys are currency codes and values are detailed market value summaries, including positions, cash balances, and PnL across multiple asset classes.

       * ``--account``: The target account ID (Required)

   * - ``set_active``
     - **Set the active dynamic account.**
       Sets a specific account as the active dynamic account for the session.

       * ``--account``: The account ID to set as active dynamic account (Required)

   * - ``funds``
     - **Retrieve a comprehensive summary of available funds.**
       Returns a comprehensive object including total funds summary and CFD specific details.

       * ``--account``: The target account ID (Required)

   * - ``list``
     - **List all accessible accounts.**
       Returns a list of account identifiers and session details.

   * - ``ownership``
     - **Retrieve comprehensive ownership details.**
       Returns an object containing user roles, entity information, and applicant signatures.
       
       * ``--account``: The target account ID (Required)

   * - ``pnl``
     - **Retrieve PnL data.**
       Fetches current session Profit and Loss across partitions.

   * - ``search``
     - **Search for dynamic accounts.**
       Returns a list of accounts matching the search pattern.

       * ``--pattern``: The pattern to use for searching accounts (Required)

   * - ``summary``
     - **Retrieve a comprehensive summary of account values.**
       Returns a comprehensive object including account type, status, balances, margins, and cash balances across different currencies.

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
