ibkr.ibkr\_watchlist package
============================

The ``ibkr_watchlist`` tool provides a comprehensive interface for managing and viewing Interactive Brokers watchlists. It supports both user-defined watchlists and pre-defined system watchlists.

Features
--------

- **List Watchlists**: View all available watchlist categories (USER, SYST, ALL).
- **Inspect Content**: Get detailed rows for a specific watchlist, including contract IDs and symbols.
- **Dynamic Management**: Create and delete user-defined watchlists.
- **Symbol Management**: Add or remove individual contracts from an existing watchlist using a convenient CLI interface.
- **Filtering**: Automatically filters out empty rows or spacers provided by the IBKR API.

Usage
-----

.. code-block:: bash

    # List all available watchlists
    python -m tools.ibkr.ibkr_watchlist list

    # Get details of a specific watchlist (e.g., SYST_1)
    python -m tools.ibkr.ibkr_watchlist get --id SYST_1

    # Create a new user-defined watchlist
    python -m tools.ibkr.ibkr_watchlist create --name "My Tech Stocks" --conids 265598 7653

    # Add contracts to an existing watchlist
    python -m tools.ibkr.ibkr_watchlist add --id USER_123 --conids 12087

    # Remove contracts from a watchlist
    python -m tools.ibkr.ibkr_watchlist remove --id USER_123 --conids 265598

    # Delete a user-defined watchlist
    python -m tools.ibkr.ibkr_watchlist delete --id USER_123

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command & Arguments
     - Description
   * - ``list``
     - **List all watchlists.**
       
       Retrieves summaries of user-defined (``USER``), system (``SYST``), and all available watchlists.
   * - ``get``
     - **Get Watchlist Details.**
       
       * ``--id``: The unique identifier for the watchlist (e.g., ``USER_123``, ``SYST_1``). (Required)
   * - ``create``
     - **Create a Watchlist.**
       
       * ``--name``: Descriptive name for the new watchlist. (Required)
       * ``--conids``: One or more IBKR Contract IDs (integers) to include initially. (Required)
   * - ``delete``
     - **Delete a Watchlist.**
       
       * ``--id``: The unique identifier (e.g., ``USER_123``) of the watchlist to remove. (Required)
   * - ``add``
     - **Add Contracts.**
       
       * ``--id``: Watchlist ID to modify. (Required)
       * ``--conids``: One or more IBKR Contract IDs to append. (Required)
   * - ``remove``
     - **Remove Contracts.**
       
       * ``--id``: Watchlist ID to modify. (Required)
       * ``--conids``: One or more IBKR Contract IDs to remove. (Required)

Implementation Details
----------------------

The command-line tool utilizes a fetch-modify-update pattern for the ``add`` and ``remove`` operations. This is because the underlying IBKR API (``POST /iserver/watchlist``) typically replaces the entire contents of a watchlist. The tool handles this complexity transparently for the user.

Submodules
----------

ibkr.ibkr\_watchlist.cli module
-------------------------------

.. automodule:: ibkr.ibkr_watchlist.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_watchlist.core module
--------------------------------

.. automodule:: ibkr.ibkr_watchlist.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_watchlist
   :members:
   :show-inheritance:
   :undoc-members:
