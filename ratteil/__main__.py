"""Entry point for running RatTeil as a module.

Usage:
    python -m ratteil
    python -m ratteil --help
    python -m ratteil --surahs 1,2,3 --reciters alafasy
"""

import sys

from ratteil.ratteil import ratteil


if __name__ == "__main__":
    sys.exit(ratteil())
