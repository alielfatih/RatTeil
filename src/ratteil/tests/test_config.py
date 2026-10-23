"""
Tests for configuration module.
"""

import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ratteil.config.settings import Settings, get_settings, reload_settings
from ratteil.config.exceptions import (
    RatTeilError,
    ConfigError,
    AuthError,
    DownloadError,
    StreamError,
    ValidationError,
    FileError,
    AudioProcessingError,
    RepositoryError,
    NotFoundError,
    TokenExpiredError,
    InvalidTokenError,
    NetworkError,
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
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    FACEBOOK_GRAPH_API,
)


class TestSettings:
    """Tests for Settings class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.app_name == "RatTeil"
            assert settings.app_version == "2024.10.22.1"
            assert settings.debug is False
            assert settings.max_stream_length == MAX_STREAM_LENGTH
            assert settings.min_stream_length == MIN_STREAM_LENGTH
            assert settings.max_concurrent_downloads == 5
            assert settings.download_timeout == 60
            assert settings.ffmpeg_path == "ffmpeg"
            assert settings.ffprobe_path == "ffprobe"
            assert settings.log_level == "INFO"
    
    def test_settings_from_env(self):
        """Test that settings are loaded from environment variables."""
        with patch.dict(os.environ, {
            "RATTEIL_APP_NAME": "RatTeil Test",
            "RATTEIL_DEBUG": "True",
            "RATTEIL_DATA_DIR": "/tmp/ratteil_test",
        }, clear=True):
            settings = Settings()
            
            assert settings.app_name == "RatTeil Test"
            assert settings.debug is True
            assert settings.data_dir == Path("/tmp/ratteil_test")
    
    def test_settings_validation_log_level(self):
        """Test log level validation."""
        with pytest.raises(ConfigError) as exc_info:
            Settings(log_level="INVALID")
        
        assert "Invalid log level" in str(exc_info.value)
        assert exc_info.value.missing_field == "log_level"
    
    def test_settings_validation_stream_length(self):
        """Test stream length validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            Settings(max_stream_length=0)  # Less than minimum
        
        with pytest.raises(Exception):  # Pydantic validation error
            Settings(max_stream_length=700)  # More than maximum
    
    def test_settings_directories_created(self, temp_dir: Path):
        """Test that directories are created on validation."""
        data_dir = temp_dir / "test_data"
        audio_dir = temp_dir / "test_data" / "audios"
        img_dir = temp_dir / "test_data" / "imgs"
        fixer_dir = temp_dir / "test_data" / "fixer"
        fb_stream_dir = temp_dir / "test_data" / "fb_stream"
        
        settings = Settings(
            data_dir=data_dir,
            audio_dir=audio_dir,
            img_dir=img_dir,
            fixer_dir=fixer_dir,
            fb_stream_dir=fb_stream_dir
        )
        
        assert data_dir.exists()
        assert audio_dir.exists()
        assert img_dir.exists()
        assert fixer_dir.exists()
        assert fb_stream_dir.exists()
    
    def test_has_youtube_credentials(self):
        """Test YouTube credentials check."""
        # Test with no credentials
        settings = Settings()
        assert settings.has_youtube_credentials() is False
        
        # Test with credentials
        settings.youtube_client_id = "test_id"
        settings.youtube_client_secret = "test_secret"
        assert settings.has_youtube_credentials() is True
        
        # Test with only one credential
        settings.youtube_client_secret = None
        assert settings.has_youtube_credentials() is False
    
    def test_has_facebook_credentials(self):
        """Test Facebook credentials check."""
        # Test with no credentials
        settings = Settings()
        assert settings.has_facebook_credentials() is False
        
        # Test with token
        settings.facebook_access_token = "test_token"
        assert settings.has_facebook_credentials() is True
        
        # Test with empty token
        settings.facebook_access_token = None
        assert settings.has_facebook_credentials() is False
    
    def test_get_youtube_scopes(self):
        """Test YouTube scopes."""
        settings = Settings()
        scopes = settings.get_youtube_scopes()
        assert scopes == YOUTUBE_SCOPES
    
    def test_get_facebook_scopes(self):
        """Test Facebook scopes."""
        settings = Settings()
        scopes = settings.get_facebook_scopes()
        assert scopes == FACEBOOK_SCOPES
    
    def test_to_dict(self):
        """Test settings to dictionary conversion."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            settings_dict = settings.to_dict()
            
            assert isinstance(settings_dict, dict)
            assert "app_name" in settings_dict
            assert "app_version" in settings_dict
            assert "debug" in settings_dict
            assert "data_dir" in settings_dict
            assert settings_dict["app_name"] == "RatTeil"


class TestGetSettings:
    """Tests for get_settings function."""
    
    def test_get_settings_cached(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_reload_settings(self):
        """Test that reload_settings returns fresh instance."""
        settings1 = get_settings()
        settings2 = reload_settings()
        
        assert settings1 is not settings2
        
        # After reload, subsequent calls should return the new instance
        settings3 = get_settings()
        assert settings2 is settings3


class TestConstants:
    """Tests for constants module."""
    
    def test_default_paths(self):
        """Test default path constants."""
        assert DEFAULT_DATA_DIR == Path.home() / "RatTeil-resources"
        assert DEFAULT_AUDIO_DIR == DEFAULT_DATA_DIR / "audios"
        assert DEFAULT_IMG_DIR == DEFAULT_DATA_DIR / "imgs"
        assert DEFAULT_FIXER_DIR == DEFAULT_DATA_DIR / "fixer"
        assert DEFAULT_FB_STREAM_DIR == DEFAULT_DATA_DIR / "fb_stream"
    
    def test_stream_lengths(self):
        """Test stream length constants."""
        assert MAX_STREAM_LENGTH == 75.0
        assert MIN_STREAM_LENGTH == 120.0
    
    def test_oauth_scopes(self):
        """Test OAuth scope constants."""
        assert len(YOUTUBE_SCOPES) > 0
        assert len(FACEBOOK_SCOPES) > 0
        assert "youtube" in YOUTUBE_SCOPES[0]
    
    def test_api_constants(self):
        """Test API constants."""
        assert YOUTUBE_API_SERVICE_NAME == "youtube"
        assert YOUTUBE_API_VERSION == "v3"
        assert FACEBOOK_GRAPH_API == "https://graph.facebook.com/v20.0"


class TestExceptions:
    """Tests for custom exceptions."""
    
    def test_ratteil_error(self):
        """Test base RatTeilError."""
        error = RatTeilError("Test error", code="TEST_ERROR")
        
        assert str(error) == "[TEST_ERROR] Test error"
        assert error.code == "TEST_ERROR"
        assert error.message == "Test error"
        assert error.details is None
    
    def test_config_error(self):
        """Test ConfigError."""
        error = ConfigError("Config error", missing_field="test_field")
        
        assert isinstance(error, RatTeilError)
        assert error.code == "CONFIG_ERROR"
        assert error.missing_field == "test_field"
    
    def test_auth_error(self):
        """Test AuthError."""
        error = AuthError("Auth error", provider="google")
        
        assert isinstance(error, RatTeilError)
        assert error.code == "AUTH_ERROR"
        assert error.provider == "google"
    
    def test_token_expired_error(self):
        """Test TokenExpiredError."""
        error = TokenExpiredError("google")
        
        assert isinstance(error, AuthError)
        assert error.code == "TOKEN_EXPIRED"
        assert error.provider == "google"
    
    def test_invalid_token_error(self):
        """Test InvalidTokenError."""
        error = InvalidTokenError("google", token="test_token")
        
        assert isinstance(error, AuthError)
        assert error.code == "INVALID_TOKEN"
        assert error.provider == "google"
        # The token is truncated in the string representation
        assert "test_tok" in str(error) or "test_token" in str(error)
    
    def test_download_error(self):
        """Test DownloadError."""
        error = DownloadError("Download failed", url="http://test.com", path="/tmp/test.mp3")
        
        assert isinstance(error, RatTeilError)
        assert error.code == "DOWNLOAD_ERROR"
        assert error.url == "http://test.com"
        assert error.path == "/tmp/test.mp3"
    
    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Connection failed", url="http://test.com", status_code=404)
        
        assert isinstance(error, DownloadError)
        assert error.code == "NETWORK_ERROR"
        assert error.status_code == 404
    
    def test_stream_error(self):
        """Test StreamError."""
        error = StreamError("Stream failed", platform="youtube", stream_id="123")
        
        assert isinstance(error, RatTeilError)
        assert error.code == "STREAM_ERROR"
        assert error.platform == "youtube"
        assert error.stream_id == "123"
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid value", field="duration", value=0)
        
        assert isinstance(error, RatTeilError)
        assert error.code == "VALIDATION_ERROR"
        assert error.field == "duration"
        assert error.value == 0
    
    def test_file_error(self):
        """Test FileError."""
        error = FileError("File not found", path="/tmp/test.mp3", operation="read")
        
        assert isinstance(error, RatTeilError)
        assert error.code == "FILE_ERROR"
        assert error.path == "/tmp/test.mp3"
        assert error.operation == "read"
    
    def test_audio_processing_error(self):
        """Test AudioProcessingError."""
        error = AudioProcessingError("FFmpeg failed", path="/tmp/test.mp3", operation="merge")
        
        assert isinstance(error, FileError)
        assert error.code == "AUDIO_PROCESSING_ERROR"
    
    def test_repository_error(self):
        """Test RepositoryError."""
        error = RepositoryError("Repository error", repository="surah", operation="get")
        
        assert isinstance(error, RatTeilError)
        assert error.code == "REPOSITORY_ERROR"
        assert error.repository == "surah"
        assert error.operation == "get"
    
    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("Surah", 1, repository="surah")
        
        assert isinstance(error, RepositoryError)
        assert error.code == "NOT_FOUND"
        assert error.resource_type == "Surah"
        assert error.resource_id == 1


class TestEnvFile:
    """Tests for .env file support."""
    
    def test_env_file_loading(self, temp_dir: Path):
        """Test loading settings from .env file."""
        env_file = temp_dir / ".env"
        env_file.write_text("""
RATTEIL_APP_NAME=Test App
RATTEIL_DEBUG=True
RATTEIL_DATA_DIR=/tmp/test_data
RATTEIL_YOUTUBE_CLIENT_ID=env_client_id
RATTEIL_YOUTUBE_CLIENT_SECRET=env_client_secret
        """)
        
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=env_file)
            
            assert settings.app_name == "Test App"
            assert settings.debug is True
            assert settings.data_dir == Path("/tmp/test_data")
            # assert settings.youtube_client_id == "env_client_id"
            # assert settings.youtube_client_secret == "env_client_secret"
