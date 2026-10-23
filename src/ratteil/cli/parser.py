"""
Argument parser for RatTeil CLI.

This module provides argument parsing for the RatTeil command-line interface.
"""

import argparse
import random as r
from typing import List


def create_parser(reciters_codes: List[str]) -> argparse.ArgumentParser:
    """
    Create the argument parser for RatTeil CLI.
    
    Args:
        reciters_codes: List of available reciter codes
        
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="RatTeil",
        description="Stream The Holy Quran to a YouTube channel.",
        epilog="""
    RatTeil  Copyright (C) 2024  Ali Elfatih. \n
    This program comes with ABSOLUTELY NO WARRANTY. \n
    This is free software, and you are welcome to redistribute it under certain conditions; \n \t type `ratteil -c' for details.
    Made with \u2661 & ^_^ by Moddaker Team""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # General options
    parser.add_argument(
        "-c", "--copyright",
        help="Show Copyright LICENSE.",
        action="store_const",
        const=True,
        dest="copyright"
    )
    parser.add_argument(
        "-l", "--list",
        metavar="",
        help="List available reciters",
        action="store_const",
        const=True,
        default=False,
        dest="reciters_list"
    )
    
    # Stream configuration
    parser.add_argument(
        "-mx", "--max",
        metavar="",
        help="Max stream length in minutes",
        type=float,
        default=450,
        dest="max_len"
    )
    parser.add_argument(
        "-m", "--min",
        metavar="",
        type=float,
        help="Minimum streams length in minutes",
        default=120.0,
        dest="minimum_stream_length"
    )
    parser.add_argument(
        "-ms", "--streams",
        metavar="",
        type=float,
        help="Minimum streams number. Note that each stream'll be 75 minute or less",
        dest="stream_numbers"
    )
    parser.add_argument(
        "-n",
        metavar="",
        type=int,
        help="Number of reciters per stream",
        default=r.randrange(3, 7),
        dest="reciters_number"
    )
    
    # Content selection
    parser.add_argument(
        "-R", "--reciter",
        metavar="",
        help="Choose reciter or reciters by code",
        dest="reciter",
        nargs="*",
        choices=reciters_codes
    )
    parser.add_argument(
        "-r", "--resume",
        metavar="",
        help="Resume previous stream",
        action="store_const",
        const=True,
        default=False,
        dest="resume_stream"
    )
    parser.add_argument(
        "-sn",
        metavar="",
        type=int,
        help="Surahs number per stream",
        default=r.randrange(20, 50),
        dest="surahs_number"
    )
    parser.add_argument(
        "-s", "--surah",
        metavar="",
        type=int,
        choices=list(range(1, 115)),
        help="Choose surah by index",
        dest="surah"
    )
    
    # Behavior options
    parser.add_argument(
        "--no-download",
        metavar="",
        default=False,
        help="Stream existing files; no new downloads",
        dest="no_download",
        action='store_const',
        const=True
    )
    parser.add_argument(
        "--no-validation",
        metavar="",
        help="Stop minimum streams validation",
        default=False,
        action="store_const",
        const=True,
        dest="no_validation"
    )
    
    # Platform selection
    parser.add_argument(
        "-t", "--sites",
        metavar="",
        help="Site to stream to",
        dest="sites",
        choices=["youtube", "yt", "fb", "facebook"],
        nargs="*"
    )
    
    # Development mode
    parser.add_argument(
        "-d", "--dev",
        dest="dev",
        action="store_const",
        const=True
    )
    
    return parser
