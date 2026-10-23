"""
CLI commands for RatTeil application.

This module contains the command handlers for the CLI.
"""

import glob as g
import time
import sys
import os
from pathlib import Path
from typing import Optional, List

from ratteil.services.stream_service import StreamService
from ratteil.services.randomizer_service import RandomizerService
from ratteil.services.download_service import DownloadService
from ratteil.utils.validation import stream_validation
from ratteil.config.settings import get_settings
from ratteil.config.exceptions import StreamError
from ratteil.utils.logging import get_logger


logger = get_logger("ratteil.cli.commands")


def pre_launcher(
    options: any,
    reciters_db: dict,
    reciters_codes_db: List[str],
    resources_path: Path,
    package_path: Path
) -> None:
    """
    Prepare and launch streaming.
    
    This is the main entry point for streaming operations.
    
    Args:
        options: Parsed command line options
        reciters_db: Reciters database
        reciters_codes_db: List of reciter codes
        resources_path: Resources directory
        package_path: Package directory
    """
    settings = get_settings()
    
    stream_service = StreamService(
        reciters_db,
        resources_path,
        package_path,
        settings
    )
    temp_reciters_list = []
    surah_index = options.surah
    
    if options.reciter:
        temp_reciters_list = options.reciter
    else:
        temp_reciters_list = reciters_codes_db
    
    selected_surahs_list = []
    download_service = DownloadService()
    
    if not options.no_download:
        _, selected_surahs_list = RandomizerService.generate_random_reciters_list(
            options.reciters_number, temp_reciters_list, reciters_db
        )
        stream_surahs_list = RandomizerService.generate_random_surahs_list(
            options.surahs_number, surah_index, selected_surahs_list
        )
        
        # Run async download_audios synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            previous_len, max_st = loop.run_until_complete(
                download_service.download_audios(
                    settings.max_stream_length,
                    stream_surahs_list,
                    reciters_db,
                    resources_path
                )
            )
        finally:
            loop.close()
        
        if not options.no_validation:
            minimum_stream_length = 0
            if options.stream_numbers:
                minimum_stream_length = options.stream_numbers * 75.0
            elif options.surahs_number:
                minimum_stream_length = 0
            else:
                minimum_stream_length = options.minimum_stream_length
            
            if not max_st:
                stream_validation(
                    stream_service,
                    settings.max_stream_length,
                    g.glob(f"{resources_path}/audios/*"),
                    minimum_stream_length,
                    temp_reciters_list,
                    previous_len,
                    surah_index,
                    reciters_db,
                    resources_path
                )
    
    launcher(stream_service, sites=options.sites)


def launcher(stream_service: StreamService, sites: List[str]) -> None:
    """
    Launch the streaming process.
    
    Args:
        stream_service: Stream service instance
        sites: List of platforms to stream to
    """
    settings = get_settings()
    stream_service.prepare_stream_files(
        g.glob(f"{stream_service.resources_path}/audios/*")
    )
    
    for stream in stream_service.streams:
        stream_service.generate_stream_details(stream)
        stream_service.stream(stream, sites)
        time.sleep(60)


def handle_reciters_list(
    reciters_db: dict,
    reciters_codes_db: List[str],
    resources_path: Path,
    package_path: Path
) -> None:
    """
    Handle the reciters list command.
    
    Args:
        reciters_db: Reciters database
        reciters_codes_db: List of reciter codes
        resources_path: Resources directory
        package_path: Package directory
    """
    reciters_list = RandomizerService.get_available_reciters_list(
        reciters_codes_db, reciters_db
    )
    reciters_list.sort()
    for reciter in reciters_list:
        print(reciter)


def handle_copyright(ratteil_path: Path) -> None:
    """
    Handle the copyright command.
    
    Args:
        ratteil_path: RatTeil package path
    """
    copyright_file_path = ratteil_path / "LICENSE"
    if copyright_file_path.exists():
        with open(copyright_file_path, "r", encoding="utf-8") as f:
            for line in f:
                print(line, end="")
    sys.exit(0)
