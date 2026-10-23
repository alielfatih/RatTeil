"""
Pytest configuration and fixtures for RatTeil tests.
"""

import os
import sys
from pathlib import Path
from typing import Generator, Any
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def test_data_dir(temp_dir: Path) -> Path:
    """Create a test data directory structure."""
    data_dir = temp_dir / "ratteil_test"
    data_dir.mkdir()
    (data_dir / "audios").mkdir()
    (data_dir / "imgs").mkdir()
    (data_dir / "fixer").mkdir()
    (data_dir / "fb_stream").mkdir()
    return data_dir


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    with patch.dict(os.environ, {
        "RATTEIL_DATA_DIR": "/tmp/ratteil_test",
        "RATTEIL_DEBUG": "True",
        "RATTEIL_MAX_STREAM_LENGTH": "75",
        "RATTEIL_MIN_STREAM_LENGTH": "120",
    }):
        from ratteil.config.settings import reload_settings
        return reload_settings()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "RATTEIL_APP_NAME": "RatTeil Test",
        "RATTEIL_DEBUG": "True",
        "RATTEIL_DATA_DIR": "/tmp/ratteil_test",
        "YOUTUBE_CLIENT_ID": "test_client_id",
        "YOUTUBE_CLIENT_SECRET": "test_client_secret",
        "FACEBOOK_ACCESS_TOKEN": "test_fb_token",
        "FACEBOOK_APP_SECRET": "test_fb_secret",
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars


@pytest.fixture
def mock_credentials_file(temp_dir: Path) -> Path:
    """Create a mock credentials file."""
    creds_file = temp_dir / "credentials.json"
    creds_file.write_text('{"access_token": "test_token", "refresh_token": "test_refresh"}')
    return creds_file


@pytest.fixture
def mock_audio_file(temp_dir: Path) -> Path:
    """Create a mock audio file."""
    audio_file = temp_dir / "test.mp3"
    # Create a minimal valid MP3 file (empty for testing)
    audio_file.write_bytes(b"ID3")
    return audio_file


@pytest.fixture
def mock_reciters_db() -> dict:
    """Create mock reciters database."""
    return {
        "alafasy": {
            "name": "Mishary Rashid Alafasy",
            "moshaf": [
                {
                    "moshaf_type": 1,
                    "name": "Murattal",
                    "server": "https://server1.quran.com/alafasy/",
                    "surah_list": "1,2,3,4,5"
                }
            ]
        },
        "husary": {
            "name": "Abdul Basit Abdus Samad",
            "moshaf": [
                {
                    "moshaf_type": 1,
                    "name": "Murattal",
                    "server": "https://server1.quran.com/husary/",
                    "surah_list": "1,2,3,4,5,6,7,8,9,10"
                }
            ]
        }
    }


@pytest.fixture
def mock_reciters_codes() -> list:
    """Create mock reciters codes list."""
    return ["alafasy", "husary"]


@pytest.fixture
def mock_surahs_db() -> dict:
    """Create mock surahs database."""
    return {
        "surah_1": {"name": "Al-Fatiha", "index": 1},
        "surah_2": {"name": "Al-Baqarah", "index": 2},
        "surah_3": {"name": "Aal-Imran", "index": 3},
    }


@pytest.fixture(autouse=True)
def reset_lru_cache():
    """Reset LRU cache before each test."""
    from ratteil.config.settings import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
