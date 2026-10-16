"""Application settings using pure Python (no external dependencies).

This module provides a simple settings class that loads configuration
from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import List, Optional


class Settings:
    """Application settings loaded from environment variables.
    
    All settings can be configured via environment variables or use defaults.
    """
    
    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "RatTeil")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    
    # Path settings
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
    AUDIO_DIR: Path = Path(os.getenv("AUDIO_DIR", "audio"))
    STREAM_DIR: Path = Path(os.getenv("STREAM_DIR", "stream"))
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", "logs"))
    
    # API Keys (should be provided via environment variables)
    RATTEIL_AC: Optional[str] = os.getenv("RATTEIL_AC")
    RATTEIL_SE: Optional[str] = os.getenv("RATTEIL_SE")
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    
    # YouTube OAuth
    YOUTUBE_CLIENT_SECRETS: Optional[str] = os.getenv("YOUTUBE_CLIENT_SECRETS")
    YOUTUBE_CREDENTIALS_FILE: Optional[str] = os.getenv("YOUTUBE_CREDENTIALS_FILE")
    
    # API endpoints
    QURAN_API_BASE: str = os.getenv("QURAN_API_BASE", "https://api.quran.com/api/v4")
    
    # Stream settings
    STREAM_TITLE: str = os.getenv("STREAM_TITLE", "RatTeil Stream")
    STREAM_DESCRIPTION: str = os.getenv("STREAM_DESCRIPTION", "Automated Quran recitation stream")
    STREAM_CATEGORY: str = os.getenv("STREAM_CATEGORY", "28")  # Religion category for YouTube
    
    # Audio settings
    AUDIO_FORMAT: str = os.getenv("AUDIO_FORMAT", "mp3")
    AUDIO_BITRATE: str = os.getenv("AUDIO_BITRATE", "192k")
    MAX_AUDIO_LENGTH: int = int(os.getenv("MAX_AUDIO_LENGTH", "3600"))  # 1 hour in seconds
    
    # Randomization settings
    MAX_RECITERS: int = int(os.getenv("MAX_RECITERS", "5"))
    MAX_SURAHS: int = int(os.getenv("MAX_SURAHS", "10"))
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Create a Settings instance from environment variables.
        
        Returns:
            Settings instance with values from environment
        """
        return cls()
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary.
        
        Returns:
            Dictionary of all settings
        """
        return {
            "APP_NAME": self.APP_NAME,
            "APP_VERSION": self.APP_VERSION,
            "DEBUG": self.DEBUG,
            "DATA_DIR": str(self.DATA_DIR),
            "AUDIO_DIR": str(self.AUDIO_DIR),
            "STREAM_DIR": str(self.STREAM_DIR),
            "LOG_DIR": str(self.LOG_DIR),
            "QURAN_API_BASE": self.QURAN_API_BASE,
            "STREAM_TITLE": self.STREAM_TITLE,
            "STREAM_DESCRIPTION": self.STREAM_DESCRIPTION,
            "STREAM_CATEGORY": self.STREAM_CATEGORY,
            "AUDIO_FORMAT": self.AUDIO_FORMAT,
            "AUDIO_BITRATE": self.AUDIO_BITRATE,
            "MAX_AUDIO_LENGTH": self.MAX_AUDIO_LENGTH,
            "MAX_RECITERS": self.MAX_RECITERS,
            "MAX_SURAHS": self.MAX_SURAHS,
        }


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the settings singleton.
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def reset_settings() -> None:
    """Reset the settings singleton (useful for testing)."""
    global _settings
    _settings = None
