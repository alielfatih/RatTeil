"""
Utilities for RatTeil application.
"""

from ratteil.utils.file_utils import (
    surah_index_to_filename,
    filename_resolve,
)
from ratteil.utils.validation import stream_validation
from ratteil.utils.logging import (
    get_logger,
    RatTeilLogger,
    trace,
    verbose,
    debug,
    info,
    warning,
    error,
    critical,
    exception,
)
from ratteil.utils.platform import (
    get_platform,
    is_linux,
    is_windows,
    is_mac,
    is_android,
    is_ios,
    get_ffmpeg_path,
    get_ffprobe_path,
    verify_ffmpeg,
    verify_ffprobe,
    run_command,
    get_temp_dir,
    get_cache_dir,
    get_data_dir,
)

__all__ = [
    "surah_index_to_filename",
    "filename_resolve",
    "stream_validation",
    "get_logger",
    "RatTeilLogger",
    "trace",
    "verbose",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "get_platform",
    "is_linux",
    "is_windows",
    "is_mac",
    "is_android",
    "is_ios",
    "get_ffmpeg_path",
    "get_ffprobe_path",
    "verify_ffmpeg",
    "verify_ffprobe",
    "run_command",
    "get_temp_dir",
    "get_cache_dir",
    "get_data_dir",
]
