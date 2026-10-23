"""
Pydantic-based settings for RatTeil application.

This module provides environment-based configuration management with:
- Type validation
- Default values
- .env file support
- Environment variable support
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator
from typing_extensions import Literal

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
from ratteil.config.exceptions import ConfigError


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    Priority (highest to lowest):
    1. Environment variables
    2. .env file
    3. Default values
    """
    
    # Application
    app_name: str = Field(default="RatTeil")
    app_version: str = Field(default="2024.10.22.1")
    debug: bool = Field(default=False)
    
    # Directories
    data_dir: Path = Field(default=DEFAULT_DATA_DIR)
    audio_dir: Path = Field(default=DEFAULT_AUDIO_DIR)
    img_dir: Path = Field(default=DEFAULT_IMG_DIR)
    fixer_dir: Path = Field(default=DEFAULT_FIXER_DIR)
    fb_stream_dir: Path = Field(default=DEFAULT_FB_STREAM_DIR)
    
    # YouTube Authentication
    youtube_client_id: Optional[str] = Field(default=None)
    youtube_client_secret: Optional[str] = Field(default=None)
    youtube_refresh_token: Optional[str] = Field(default=None)
    youtube_access_token: Optional[str] = Field(default=None)
    youtube_token_expiry: Optional[int] = Field(default=None)
    
    # Facebook Authentication
    facebook_access_token: Optional[str] = Field(default=None)
    facebook_app_secret: Optional[str] = Field(default=None)
    facebook_page_id: Optional[str] = Field(default=None)
    
    # Streaming Configuration
    max_stream_length: float = Field(default=MAX_STREAM_LENGTH, ge=1.0, le=600.0)
    min_stream_length: float = Field(default=MIN_STREAM_LENGTH, ge=1.0, le=600.0)
    
    # Download Configuration
    max_concurrent_downloads: int = Field(default=5, ge=1, le=20)
    download_timeout: int = Field(default=60, ge=10, le=300)
    
    # FFmpeg Configuration
    ffmpeg_path: str = Field(default="ffmpeg")
    ffprobe_path: str = Field(default="ffprobe")
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_file: Optional[Path] = Field(default=None)
    
    # Data Configuration
    data_language: str = Field(default="ar")
    data_offline: bool = Field(default=False)
    
    # Randomization Configuration
    default_reciters_count: int = Field(default=5, ge=1, le=20)
    default_surahs_count: int = Field(default=30, ge=1, le=114)
    
    # API Configuration
    api_base_url: str = Field(default="https://api.quran.com")
    
    # Platform-specific settings
    platform: Optional[str] = Field(default=None)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="RATTEIL_",
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ConfigError(
                f"Invalid log level: {v}. Must be one of {valid_levels}",
                missing_field="log_level"
            )
        return v.upper()
    
    @field_validator("data_language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate data language."""
        # Allow any language code (will be validated by API)
        return v.lower()
    
    @field_validator("data_dir", "audio_dir", "img_dir", "fixer_dir", "fb_stream_dir")
    @classmethod
    def create_directories(cls, v: Path) -> Path:
        """Create directories if they don't exist."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator("facebook_access_token")
    @classmethod
    def validate_facebook_token(cls, v: Optional[str]) -> Optional[str]:
        """Validate Facebook token format."""
        if v and len(v) < 10:
            raise ConfigError(
                f"Facebook access token seems too short: {len(v)} characters",
                missing_field="facebook_access_token"
            )
        return v
    
    @model_validator(mode="after")
    def validate_youtube_credentials(self) -> "Settings":
        """Validate YouTube credentials are provided together if any is provided."""
        if (self.youtube_client_id or self.youtube_client_secret) and not \
           (self.youtube_client_id and self.youtube_client_secret):
            raise ConfigError(
                "Both YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET must be provided",
                missing_field="youtube_client_id,youtube_client_secret"
            )
        return self
    
    def get_youtube_scopes(self) -> List[str]:
        """Get YouTube OAuth scopes."""
        return YOUTUBE_SCOPES
    
    def get_facebook_scopes(self) -> List[str]:
        """Get Facebook OAuth scopes."""
        return FACEBOOK_SCOPES
    
    def has_youtube_credentials(self) -> bool:
        """Check if YouTube credentials are configured."""
        return bool(self.youtube_client_id and self.youtube_client_secret)
    
    def has_facebook_credentials(self) -> bool:
        """Check if Facebook credentials are configured."""
        return bool(self.facebook_access_token)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "debug": self.debug,
            "data_dir": str(self.data_dir),
            "audio_dir": str(self.audio_dir),
            "img_dir": str(self.img_dir),
            "fixer_dir": str(self.fixer_dir),
            "fb_stream_dir": str(self.fb_stream_dir),
            "max_stream_length": self.max_stream_length,
            "min_stream_length": self.min_stream_length,
            "max_concurrent_downloads": self.max_concurrent_downloads,
            "download_timeout": self.download_timeout,
            "ffmpeg_path": self.ffmpeg_path,
            "ffprobe_path": self.ffprobe_path,
            "log_level": self.log_level,
            "log_file": str(self.log_file) if self.log_file else None,
            "default_reciters_count": self.default_reciters_count,
            "default_surahs_count": self.default_surahs_count,
            "data_language": self.data_language,
            "data_offline": self.data_offline,
            "has_youtube_credentials": self.has_youtube_credentials(),
            "has_facebook_credentials": self.has_facebook_credentials(),
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: The application settings.
    
    Note:
        This function caches the settings instance. To reload settings,
        call `get_settings.cache_clear()`.
    """
    return Settings()


def reload_settings() -> Settings:
    """
    Reload settings from environment variables and .env file.
    
    Returns:
        Settings: Fresh settings instance.
    """
    get_settings.cache_clear()
    return get_settings()
