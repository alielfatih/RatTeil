"""
Constants for RatTeil application.
"""

from pathlib import Path
from typing import List

# Default directories
DEFAULT_DATA_DIR: Path = Path.home() / "RatTeil-resources"
DEFAULT_AUDIO_DIR: Path = DEFAULT_DATA_DIR / "audios"
DEFAULT_IMG_DIR: Path = DEFAULT_DATA_DIR / "imgs"
DEFAULT_FIXER_DIR: Path = DEFAULT_DATA_DIR / "fixer"
DEFAULT_FB_STREAM_DIR: Path = DEFAULT_DATA_DIR / "fb_stream"

# Default stream lengths (in minutes)
MAX_STREAM_LENGTH: float = 75.0
MIN_STREAM_LENGTH: float = 120.0

# OAuth scopes
YOUTUBE_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]

FACEBOOK_SCOPES: List[str] = [
    "pages_manage_engagement",
    "pages_read_engagement",
    "public_profile",
]

# API endpoints
YOUTUBE_API_SERVICE_NAME: str = "youtube"
YOUTUBE_API_VERSION: str = "v3"
FACEBOOK_GRAPH_API: str = "https://graph.facebook.com/v20.0"

# File patterns
AUDIO_FILE_PATTERN: str = "*.mp3"
IMAGE_FILE_PATTERN: str = "*.png"
STREAM_KEY_FILE: str = "stream_key.txt"

# FFmpeg settings
FFMPEG_VIDEO_BITRATE: str = "800k"
FFMPEG_AUDIO_BITRATE: str = "128k"
FFMPEG_FRAME_RATE: str = "30"
FFMPEG_RESOLUTION: str = "1080p"

# Retry settings
MAX_RETRY_ATTEMPTS: int = 3
RETRY_BACKOFF_FACTOR: float = 2.0

# Timeouts
HTTP_TIMEOUT: int = 30
DOWNLOAD_TIMEOUT: int = 60
STREAM_TIMEOUT: int = 300

# Validation
MIN_AUDIO_DURATION: float = 0.1  # Minimum audio duration in minutes
MAX_AUDIO_DURATION: float = 75.0  # Maximum audio duration in minutes
