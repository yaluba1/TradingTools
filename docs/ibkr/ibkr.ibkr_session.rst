ibkr.ibkr\_session package
==========================

The ``ibkr_session`` tool provides a comprehensive interface for managing and tracking your Interactive Brokers Web API sessions. Beyond basic API operations, this tool implements persistent session lifecycle tracking in a local MariaDB database.

Features
--------

- **Status Monitoring**: Check the current authentication and connection status of the IBKR Gateway.
- **Session Lifecycle Tracking**: Automatically records session start and end times in the ``ibkr_sessions`` database table.
- **Session Intelligence**: Automatically detects session timeouts. If the database records a session as active but the Gateway reports it is unauthenticated, the tool marks the database record as ``EXPIRED``.
- **Keep-Alive**: Send heartbeat "tickle" requests to prevent session timeouts (sessions typically expire after 5 minutes of inactivity).
- **Session Initialization**: Manually trigger brokerage session initialization for trading.
- **Logout**: Gracefully terminate the current session and update the database tracking record.

Usage
-----

.. code-block:: bash

    # Check current session status
    python -m tools.ibkr.ibkr_session status

    # Initialize brokerage session
    python -m tools.ibkr.ibkr_session init

    # Keep session alive
    python -m tools.ibkr.ibkr_session tickle

    # Logout and record session end
    python -m tools.ibkr.ibkr_session logout

Detailed Command Reference
--------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Command
     - Description
   * - ``status``
     - **Check Session Status.**
       
       Retrieves authentication and connectivity status.
       
       **Side Effect**: If a session was recorded as ``ACTIVE`` in the DB but the API reports ``authenticated: false``, the DB record is updated to ``EXPIRED``.
   * - ``init``
     - **Initialize Session.**
       
       Requests initialization of the brokerage session.
       
       **Side Effect**: Records a new ``ACTIVE`` session in the ``ibkr_sessions`` table. Any previous active session is marked as ``SUPERSEDED``.
   * - ``logout``
     - **Logout.**
       
       Terminates the current Gateway session.
       
       **Side Effect**: Marks the active DB session record as ``LOGGED_OUT``.
   * - ``tickle``
     - **Send Heartbeat.**
       
       Sends a request to the ``/tickle`` endpoint. Must be called at least once every 5 minutes to prevent the Gateway from timing out.
   * - ``reauth``
     - **Re-authenticate.**
       
       Triggers a re-authentication flow with the Gateway.

Session Database Schema
-----------------------

The tool uses the ``ibkr_sessions`` table to track session durations:

- **start_time_utc**: Timestamp when the session was created or detected.
- **end_time_utc**: Timestamp when the session ended or was found to be expired.
- **status**:
    - ``ACTIVE``: The session is currently authenticated and valid.
    - ``EXPIRED``: The session timed out or was detected as lost during a status check.
    - ``LOGGED_OUT``: The user explicitly called the ``logout`` command.
    - ``SUPERSEDED``: A new session was started before the old one was formally closed.

Submodules
----------

ibkr.ibkr\_session.cli module
-----------------------------

.. automodule:: ibkr.ibkr_session.cli
   :members:
   :show-inheritance:
   :undoc-members:

ibkr.ibkr\_session.core module
------------------------------

.. automodule:: ibkr.ibkr_session.core
   :members:
   :show-inheritance:
   :undoc-members:

Module contents
---------------

.. automodule:: ibkr.ibkr_session
   :members:
   :show-inheritance:
   :undoc-members:
