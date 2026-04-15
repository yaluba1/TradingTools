-- Database setup for IBKR Trading Tools
-- Run this script in the MariaDB 'ibkr_db' database.

CREATE TABLE IF NOT EXISTS ibkr_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp_utc DATETIME NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    account_id VARCHAR(255),
    alert_id VARCHAR(255),
    level VARCHAR(50) NOT NULL,
    message TEXT,
    details JSON,
    INDEX idx_timestamp (timestamp_utc),
    INDEX idx_tool (tool_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ibkr_alerts (
    order_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    alert_name VARCHAR(255) NOT NULL,
    alert_active TINYINT(1) DEFAULT 1,
    alert_triggered TINYINT(1) DEFAULT 0,
    tif VARCHAR(50),
    expire_time DATETIME,
    last_sync_utc DATETIME NOT NULL,
    UNIQUE INDEX idx_account_name (account_id, alert_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ibkr_orders (
    customer_order_id VARCHAR(50) PRIMARY KEY,
    server_order_id VARCHAR(50),
    account_id VARCHAR(50) NOT NULL,
    conid INT NOT NULL,
    symbol VARCHAR(20),
    side VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    quantity DECIMAL(18, 4) NOT NULL,
    price DECIMAL(18, 4),
    aux_price DECIMAL(18, 4),
    tif VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL,
    filled_quantity DECIMAL(18, 4) DEFAULT 0,
    avg_fill_price DECIMAL(18, 4) DEFAULT 0,
    last_update_utc DATETIME NOT NULL,
    created_at_utc DATETIME NOT NULL,
    INDEX idx_server_id (server_order_id),
    INDEX idx_account_status (account_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ibkr_order_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_order_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    timestamp_utc DATETIME NOT NULL,
    data JSON,
    message TEXT,
    INDEX idx_order_id (customer_order_id),
    CONSTRAINT fk_order_cust FOREIGN KEY (customer_order_id) REFERENCES ibkr_orders(customer_order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ibkr_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_time_utc DATETIME NOT NULL,
    end_time_utc DATETIME,
    status VARCHAR(50) NOT NULL,
    account_id VARCHAR(50),
    INDEX idx_status (status),
    INDEX idx_start (start_time_utc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
