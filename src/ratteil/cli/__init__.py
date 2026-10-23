"""
CLI module for RatTeil application.
"""

from ratteil.cli.parser import create_parser
from ratteil.cli.commands import (
    pre_launcher,
    handle_reciters_list,
    handle_copyright,
    launcher,
)

__all__ = [
    "create_parser",
    "pre_launcher",
    "handle_reciters_list",
    "handle_copyright",
    "launcher",
]
