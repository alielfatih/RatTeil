"""RatTeil - Quran recitation streaming tool.

This package provides functionality for downloading, managing, and streaming
Quran recitations from various reciters.
"""

from .config import get_settings, reset_settings
from .config.exceptions import (
    RatTeilError,
    ConfigurationError,
    DownloadError,
    StreamError,
    ValidationError,
    AudioMergeError,
    YouTubeError,
)
from .models import Surah, SurahInfo, Reciter, Moshaf, StreamDetails, StreamFile
from .repositories import (
    ReciterRepository,
    LocalReciterRepository,
    SurahRepository,
    LocalSurahRepository,
)
from .services import (
    AudioService,
    DownloadService,
    StreamService,
    YouTubeService,
    RandomizerService,
)
from .utils import (
    ensure_directory,
    cleanup_files,
    find_audio_files,
    filename_resolve,
    surah_index_to_filename,
    validate_audio_file,
    validate_surah_id,
    validate_reciter_id,
    validate_stream_details,
    get_logger,
    setup_logging,
)
from .cli import create_parser, parse_args, run_ratteil


__version__ = "1.0.0"
__author__ = "RatTeil Team"
__description__ = "Quran recitation streaming tool"


def ratteil() -> int:
    """Main entry point for the RatTeil application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    from .cli.parser import parse_args
    from .cli.commands import run_ratteil
    
    args = parse_args()
    return run_ratteil(args)
