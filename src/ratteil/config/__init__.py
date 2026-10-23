"""
Configuration module for RatTeil.
"""

from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import (
    RatTeilError,
    ConfigError,
    AuthError,
    DownloadError,
    StreamError,
    ValidationError,
)
from ratteil.config.constants import (
    DEFAULT_DATA_DIR,
    DEFAULT_AUDIO_DIR,
    DEFAULT_IMG_DIR,
    DEFAULT_FIXER_DIR,
    DEFAULT_FB_STREAM_DIR,
    MAX_STREAM_LENGTH,
    MIN_STREAM_LENGTH,
    YOUTUBE_SCOPES,
    FACEBOOK_SCOPES,
)

__all__ = [
    "Settings",
    "get_settings",
    "RatTeilError",
    "ConfigError",
    "AuthError",
    "DownloadError",
    "StreamError",
    "ValidationError",
    "DEFAULT_DATA_DIR",
    "DEFAULT_AUDIO_DIR",
    "DEFAULT_IMG_DIR",
    "DEFAULT_FIXER_DIR",
    "DEFAULT_FB_STREAM_DIR",
    "MAX_STREAM_LENGTH",
    "MIN_STREAM_LENGTH",
    "YOUTUBE_SCOPES",
    "FACEBOOK_SCOPES",
]
