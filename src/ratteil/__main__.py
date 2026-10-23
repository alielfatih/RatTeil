"""
Main entry point for RatTeil package.

This module allows running RatTeil as a module: python -m ratteil
"""

import sys

# Run the CLI
from ratteil.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
