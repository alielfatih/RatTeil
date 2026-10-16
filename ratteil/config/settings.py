"""Application settings using Pydantic for validation."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field, HttpUrl


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME: str = "RatTeil"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Path settings
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = Field(default_factory=lambda: Path("data"))
    AUDIO_DIR: Path = Field(default_factory=lambda: Path("audio"))
    STREAM_DIR: Path = Field(default_factory=lambda: Path("stream"))
    LOG_DIR: Path = Field(default_factory=lambda: Path("logs"))
    
    # API Keys (should be provided via environment variables)
    RATTEIL_AC: Optional[str] = None
    RATTEIL_SE: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    
    # YouTube OAuth
    YOUTUBE_CLIENT_SECRETS: Optional[str] = None
    YOUTUBE_CREDENTIALS_FILE: Optional[str] = None
    
    # API endpoints
    QURAN_API_BASE: HttpUrl = "https://api.quran.com/api/v4"
    
    # Stream settings
    STREAM_TITLE: str = "RatTeil Stream"
    STREAM_DESCRIPTION: str = "Automated Quran recitation stream"
    STREAM_CATEGORY: str = "28"  # Religion category for YouTube
    
    # Audio settings
    AUDIO_FORMAT: str = "mp3"
    AUDIO_BITRATE: str = "192k"
    MAX_AUDIO_LENGTH: int = 3600  # 1 hour in seconds
    
    # Randomization settings
    MAX_RECITERS: int = 5
    MAX_SURAHS: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the settings singleton (useful for testing)."""
    global _settings
    _settings = None
