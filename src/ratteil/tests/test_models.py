"""
Tests for models module.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from ratteil.models.surah import SurahInfo
from ratteil.models.reciter import Reciter
from ratteil.models.stream import StreamConfig, StreamDetails
from ratteil.models.auth import OAuthToken, AuthCredentials, YouTubeCredentials, FacebookCredentials


class TestSurahInfo:
    """Tests for SurahInfo model."""
    
    @pytest.fixture
    def mock_reciters_db(self):
        """Create mock reciters database."""
        return {
            "alafasy": {
                "name": "Mishary Rashid Alafasy",
                "moshaf": [{
                    "moshaf_type": 1,
                    "name": "Murattal",
                    "server": "https://server1.quran.com/alafasy/",
                    "surah_list": "1,2,3,4,5"
                }]
            }
        }
    
    def test_surah_info_creation(self, mock_reciters_db):
        """Test creating SurahInfo instance."""
        surah = SurahInfo(
            index=1,
            code="alafasy",
            mtype=1,
            reciters_db=mock_reciters_db
        )
        
        assert surah.index == 1
        assert surah.code == "alafasy"
        assert surah.mtype == 1
        assert surah.id == "1"
        assert surah.name  # Should be set from surah_list
        assert surah.reciter is not None
        assert surah.dl_name == "alafasy@@1@@1.mp3"
    
    def test_surah_info_str(self, mock_reciters_db):
        """Test string representation of SurahInfo."""
        surah = SurahInfo(
            index=1,
            code="alafasy",
            mtype=1,
            reciters_db=mock_reciters_db
        )
        
        result = str(surah)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_surah_info_get_audio_url(self, mock_reciters_db):
        """Test getting audio URL."""
        surah = SurahInfo(
            index=1,
            code="alafasy",
            mtype=1,
            reciters_db=mock_reciters_db
        )
        
        url = surah.get_audio_url()
        assert isinstance(url, str)
        assert "001.mp3" in url or "1.mp3" in url
    
    def test_surah_info_get_filepath(self, mock_reciters_db, temp_dir: Path):
        """Test getting local filepath."""
        surah = SurahInfo(
            index=1,
            code="alafasy",
            mtype=1,
            reciters_db=mock_reciters_db
        )
        
        filepath = surah.get_filepath(temp_dir)
        assert isinstance(filepath, Path)
        assert filepath.name == "alafasy@@1@@1.mp3"


class TestReciter:
    """Tests for Reciter model."""
    
    @pytest.fixture
    def mock_reciters_db(self):
        """Create mock reciters database."""
        return {
            "alafasy": {
                "name": "Mishary Rashid Alafasy",
                "moshaf": [{
                    "moshaf_type": 1,
                    "name": "Murattal",
                    "server": "https://server1.quran.com/alafasy/",
                    "surah_list": "1,2,3,4,5"
                }]
            }
        }
    
    def test_reciter_creation(self, mock_reciters_db):
        """Test creating Reciter instance."""
        reciter = Reciter("alafasy", mock_reciters_db)
        
        assert reciter.code == "alafasy"
        assert reciter.name == "Mishary Rashid Alafasy"
        assert reciter.moshafs is not None
        assert len(reciter.moshafs) == 1
    
    def test_reciter_get_moshaf_name_url(self, mock_reciters_db):
        """Test getting moshaf name or URL."""
        reciter = Reciter("alafasy", mock_reciters_db)
        
        # Get name
        name = reciter.get_moshaf_name_url(1, url=False)
        assert name == "Murattal"
        
        # Get URL
        url = reciter.get_moshaf_name_url(1, url=True)
        assert url == "https://server1.quran.com/alafasy/"


class TestStreamConfig:
    """Tests for StreamConfig model."""
    
    def test_stream_config_defaults(self):
        """Test StreamConfig with default values."""
        config = StreamConfig()
        
        assert config.title == ""
        assert config.description == ""
        assert config.platform == "youtube"
        assert config.max_length == 75.0
        assert config.min_length == 120.0
        assert config.reciters == []
        assert config.surahs == []
    
    def test_stream_config_validation(self):
        """Test StreamConfig validation."""
        with pytest.raises(ValueError):
            StreamConfig(max_length=0)
        
        with pytest.raises(ValueError):
            StreamConfig(min_length=0)
        
        with pytest.raises(ValueError):
            StreamConfig(platform="invalid")


class TestStreamDetails:
    """Tests for StreamDetails model."""
    
    def test_stream_details_creation(self):
        """Test creating StreamDetails instance."""
        details = StreamDetails(
            stream_id="test_123",
            title="Test Stream",
            description="Test Description",
            platform="youtube"
        )
        
        assert details.stream_id == "test_123"
        assert details.title == "Test Stream"
        assert details.platform == "youtube"
        assert details.status == "pending"
        assert details.start_time is not None
        assert details.end_time is not None
    
    def test_stream_details_mark_live(self):
        """Test marking stream as live."""
        details = StreamDetails(stream_id="test_123")
        details.mark_live("https://stream.url", "stream_key_123")
        
        assert details.status == "live"
        assert details.stream_url == "https://stream.url"
        assert details.stream_key == "stream_key_123"
    
    def test_stream_details_mark_completed(self):
        """Test marking stream as completed."""
        details = StreamDetails(stream_id="test_123")
        details.mark_completed()
        
        assert details.status == "completed"
        assert details.end_time is not None
    
    def test_stream_details_mark_error(self):
        """Test marking stream as error."""
        details = StreamDetails(stream_id="test_123")
        details.mark_error("Test error")
        
        assert details.status == "error"
        assert details.error == "Test error"
    
    def test_stream_details_status_checks(self):
        """Test status check methods."""
        details = StreamDetails(stream_id="test_123")
        
        assert details.is_live() is False
        assert details.is_completed() is False
        assert details.is_error() is False
        
        details.mark_live("url", "key")
        assert details.is_live() is True
        
        details.mark_completed()
        assert details.is_completed() is True
        
        details.mark_error("error")
        assert details.is_error() is True


class TestOAuthToken:
    """Tests for OAuthToken model."""
    
    def test_oauth_token_creation(self):
        """Test creating OAuthToken instance."""
        token = OAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            token_type="Bearer",
            expires_in=3600,
            scope="read write"
        )
        
        assert token.access_token == "test_token"
        assert token.refresh_token == "test_refresh"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600
        assert token.scope == "read write"
        assert token.issued_at is not None
        assert token.expires_at is not None
    
    def test_oauth_token_expiration(self):
        """Test token expiration check."""
        # Create token that expires in the past
        past_time = datetime.now() - timedelta(hours=2)
        token = OAuthToken(
            access_token="test_token",
            expires_in=3600,
            issued_at=past_time
        )
        
        assert token.is_expired() is True
        
        # Create token that expires in the future
        future_time = datetime.now() + timedelta(hours=2)
        token = OAuthToken(
            access_token="test_token",
            expires_in=7200,
            issued_at=future_time
        )
        
        assert token.is_expired() is False
    
    def test_oauth_token_headers(self):
        """Test getting authorization header."""
        token = OAuthToken(
            access_token="test_token",
            token_type="Bearer"
        )
        
        header = token.get_authorization_header()
        assert header == "Bearer test_token"
    
    def test_oauth_token_serialization(self):
        """Test token serialization."""
        token = OAuthToken(
            access_token="test_token",
            refresh_token="test_refresh",
            token_type="Bearer",
            expires_in=3600,
            scope="read write"
        )
        
        # Test to_dict
        data = token.to_dict()
        assert data["access_token"] == "test_token"
        assert data["refresh_token"] == "test_refresh"
        
        # Test to_json
        json_str = token.to_json()
        assert isinstance(json_str, str)
        assert "test_token" in json_str
        
        # Test from_dict
        token2 = OAuthToken.from_dict(data)
        assert token2.access_token == token.access_token
        assert token2.refresh_token == token.refresh_token
        
        # Test from_json
        token3 = OAuthToken.from_json(json_str)
        assert token3.access_token == token.access_token


class TestAuthCredentials:
    """Tests for AuthCredentials model."""
    
    def test_auth_credentials_creation(self):
        """Test creating AuthCredentials instance."""
        creds = AuthCredentials(
            client_id="test_id",
            client_secret="test_secret",
            access_token="test_token",
            refresh_token="test_refresh",
            scopes=["read", "write"]
        )
        
        assert creds.client_id == "test_id"
        assert creds.client_secret == "test_secret"
        assert creds.access_token == "test_token"
        assert creds.scopes == ["read", "write"]
    
    def test_auth_credentials_has_credentials(self):
        """Test has_credentials check."""
        # With credentials
        creds = AuthCredentials(
            client_id="test_id",
            client_secret="test_secret"
        )
        assert creds.has_credentials() is True
        
        # Without credentials
        creds = AuthCredentials()
        assert creds.has_credentials() is False
    
    def test_auth_credentials_has_token(self):
        """Test has_token check."""
        # With token
        creds = AuthCredentials(access_token="test_token")
        assert creds.has_token() is True
        
        # Without token
        creds = AuthCredentials()
        assert creds.has_token() is False
    
    def test_auth_credentials_serialization(self):
        """Test credentials serialization."""
        creds = AuthCredentials(
            client_id="test_id",
            client_secret="test_secret"
        )
        
        data = creds.to_dict()
        assert data["client_id"] == "test_id"
        
        creds2 = AuthCredentials.from_dict(data)
        assert creds2.client_id == creds.client_id


class TestYouTubeCredentials:
    """Tests for YouTubeCredentials model."""
    
    def test_youtube_credentials_creation(self):
        """Test creating YouTubeCredentials instance."""
        creds = YouTubeCredentials(
            client_id="test_id",
            client_secret="test_secret"
        )
        
        assert isinstance(creds, AuthCredentials)
        assert creds.client_id == "test_id"


class TestFacebookCredentials:
    """Tests for FacebookCredentials model."""
    
    def test_facebook_credentials_creation(self):
        """Test creating FacebookCredentials instance."""
        creds = FacebookCredentials(
            app_id="test_app_id",
            app_secret="test_app_secret",
            page_id="test_page_id"
        )
        
        assert isinstance(creds, AuthCredentials)
        assert creds.app_id == "test_app_id"
        assert creds.app_secret == "test_app_secret"
        assert creds.page_id == "test_page_id"
