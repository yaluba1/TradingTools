"""
Main entry point for the IBKR Scanner tool package.
Allows running the tool using `python -m tools.ibkr.ibkr_scanner`.
"""
from .cli import main

if __name__ == "__main__":
    main()
