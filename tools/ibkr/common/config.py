"""
Configuration loading utilities for IBKR Trading Tools.
This module provides functions to load YAML configuration files for the IBKR API
and the MariaDB database from the secrets directory.
"""
import yaml
from pathlib import Path
from typing import Any, Dict

def load_yaml_config(file_path: Path) -> Dict[str, Any]:
    """
    Load a YAML configuration file from the specified path.

    Args:
        file_path (Path): The absolute or relative path to the YAML file.

    Returns:
        Dict[str, Any]: The configuration data as a dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the file is not a valid YAML.
    """
    # Check if the file exists before attempting to open it
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    # Open and parse the YAML file
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def get_ibkr_config() -> Dict[str, Any]:
    """
    Retrieve the IBKR API configuration from the default secrets location.
    The configuration is assumed to be at './secrets/ibkr.yaml'.

    Returns:
        Dict[str, Any]: The IBKR configuration dictionary containing API endpoints,
                        logging levels, and other settings.
    """
    # Define the path relative to the repository root
    config_path = Path("./secrets/ibkr.yaml")
    return load_yaml_config(config_path)

def get_db_config() -> Dict[str, Any]:
    """
    Retrieve the database configuration from the default secrets location.
    The configuration is assumed to be at './secrets/trading_db.yaml'.

    Returns:
        Dict[str, Any]: The database configuration dictionary containing host,
                        port, credentials, and database name.
    """
    config_path = Path("./secrets/trading_db.yaml")
    return load_yaml_config(config_path)
