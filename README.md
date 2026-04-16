# TradingTools

TradingTools is a comprehensive Python-based suite designed to interact with the Interactive Brokers (IBKR) Client Portal API. This repository provides a collection of self-contained tools for managing accounts, orders, portfolios, alerts, and market discovery, with built-in support for persistent logging and session tracking.

Personally, I am using this tool in MCPs and skills for AI agents. 

## Core Features

- **Pacing Compliance**: All tools respect the IBKR 10 requests per second limit.
- **Robust Validation**: Uses Pydantic schemas for all API interactions.
- **Database Persistence**: Persistent logging and session duration tracking in MariaDB.
- **Modular Design**: Each tool is a self-contained Python package.

## Implemented Tools

The following tools are available under the `tools/ibkr/` package:

- **`ibkr_accounts`**: List accounts, retrieve PnL, sub-accounts, and account ownership information.
- **`ibkr_alerts`**: Create, modify, and delete price, margin, and volume alerts.
- **`ibkr_contract`**: Search for instrument details, market rules, and option strikes via Contract IDs (Conids).
- **`ibkr_orders`**: Complete order execution lifecycle, including placement, modification, status monitoring, and answering system questions.
- **`ibkr_portfolio`**: Real-time holdings analysis, account ledgers, and historical performance analysis via Portfolio Analyst.
- **`ibkr_scanner`**: High-performance market discovery using customizable instruments, locations, and criteria.
- **`ibkr_session`**: Centralized web session management, including authentication status, keep-alives (tickle), and persistent tracking of session durations.
- **`ibkr_watchlist`**: Create and manage user-defined and system watchlists.

## Getting Started

### Prerequisites

- **Python 3.13+** (managed via [`uv`](https://docs.astral.sh/uv/))
- **MariaDB** for persistent logging and tracking.
- [**IBKR Client Portal Gateway**](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#cpgw) running on the configured port.

### Configuration (Secrets)

The tools require configuration files located in the `secrets/` directory. You must create these files using the provided templates or examples.

#### IBKR API Configuration (`secrets/ibkr.yaml`)

This file configures the connection to the IBKR Client Portal Gateway and general tool behavior:

```yaml
api:
  base_url: "https://localhost:5001/v1/api/"  # Base URL of your IBKR Gateway
  verify_ssl: false                          # Set to true if using valid SSL certs
  timeout_seconds: 30                        # API request timeout
logging:
  level: "INFO"                              # INFO, DEBUG, or ERROR
  file_path: "~/logs/ibkr.log"               # Path for persistent file logs
```

#### Database Configuration (`secrets/trading_db.yaml`)

This file contains the credentials for the MariaDB instance used for persistent logging and session tracking:

```yaml
database:
  host: "localhost"         # Database server host
  port: 3306                # Database port
  user: "trading_user"      # Authorized database user
  password: "your_password" # User password
  name: "ibkr_db"           # Database name
```

### Database Setup

To initialize the required tables for logging and session tracking, run the setup script:

```bash
mysql -u <your_user> -p < database_setup.sql
```

Ensure your database connection details are configured in `secrets/trading_db.yaml` (see the [Configuration (Secrets)](#configuration-secrets) section above).

### Building Documentation

The technical documentation is built using Sphinx. To generate the HTML version:

```bash
uv run sphinx-build -b html docs/ibkr docs/ibkr/_build/html
```

The resulting files will be available in `docs/ibkr/_build/html/index.html`.

### Running Tests

The repository includes a comprehensive suite of mock tests to verify logic without hitting live API endpoints:

```bash
# Run all IBKR mock tests
uv run pytest tests/mock_ibkr_*.py

# Run with coverage tracking
uv run pytest --cov=tools/ibkr tests/mock_ibkr_*.py
```

## Tool Usage

All tools follow a consistent execution pattern:

```bash
python -m tools.ibkr.<tool_name> <command> [arguments]
```

Use the `--help` flag with any tool to see available subcommands and arguments.

# Support

IBKR API documentation does not provide schemas for responses, so I did my best to figure out what is optional and what is mandatory. 

It works for me, but if it doesn't for you, feel free to open an issue and I will see what I can do.

## Bruno collection

A [Bruno](https://www.usebruno.com/) collection is available for local testing of each API endpoint. This can be used to verify that the tools are working correctly.
If something works with Bruno but fails in the tool, then feel free to report a bug.
