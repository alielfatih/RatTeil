"""
Tests for services module.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from ratteil.services.audio_service import AudioService
from ratteil.services.download_service import DownloadService
from ratteil.services.stream_service import StreamService
from ratteil.services.randomizer_service import RandomizerService
from ratteil.services.youtube_service import YouTubeService
from ratteil.services.facebook_service import FacebookService
from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import AudioProcessingError, DownloadError


class TestAudioService:
    """Tests for AudioService."""
    
    @pytest.fixture
    def audio_service(self):
        """Create AudioService instance."""
        return AudioService()
    
    @pytest.fixture
    def temp_audio_file(self, temp_dir: Path):
        """Create a temporary audio file."""
        audio_file = temp_dir / "test.mp3"
        # Create a minimal valid MP3 file
        # This is a placeholder - in real tests, you'd use a real audio file
        audio_file.write_bytes(b"ID3")
        return audio_file
    
    def test_get_audio_length(self, audio_service: AudioService, temp_audio_file: Path):
        """Test getting audio length."""
        # This test will fail if ffprobe is not available
        # We'll mock it for testing
        with patch('subprocess.check_output') as mock_check_output:
            mock_check_output.return_value = b"60.5\n"
            length = audio_service.get_audio_length(temp_audio_file)
            assert length == 1.0  # 60.5 seconds = 1.00833 minutes, truncated to 1.0
    
    def test_get_audio_length_file_not_found(self, audio_service: AudioService):
        """Test handling of missing file."""
        with patch('subprocess.check_output') as mock_check_output:
            mock_check_output.side_effect = FileNotFoundError()
            length = audio_service.get_audio_length("/nonexistent/file.mp3")
            assert length == 0.0
    
    def test_get_audio_length_invalid_audio(self, audio_service: AudioService, temp_audio_file: Path):
        """Test handling of invalid audio file."""
        with patch('subprocess.check_output') as mock_check_output:
            mock_check_output.side_effect = ValueError("Invalid audio")
            length = audio_service.get_audio_length(temp_audio_file)
            assert length == 0.0
            assert not temp_audio_file.exists()
    
    def test_merge_audios(self, audio_service: AudioService, temp_dir: Path):
        """Test merging audio files."""
        # Create test audio files
        audio1 = temp_dir / "audio1.mp3"
        audio2 = temp_dir / "audio2.mp3"
        audio1.write_bytes(b"ID3")
        audio2.write_bytes(b"ID3")
        
        output_dir = temp_dir / "output"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = audio_service.merge_audios([str(audio1), str(audio2)], str(output_dir))
            assert result.exists()
            assert result.name == "merged.mp3"
    
    def test_merge_audios_no_files(self, audio_service: AudioService, temp_dir: Path):
        """Test merging with no files."""
        with pytest.raises(AudioProcessingError):
            audio_service.merge_audios([], str(temp_dir))


class TestDownloadService:
    """Tests for DownloadService."""
    
    @pytest.fixture
    def download_service(self):
        """Create DownloadService instance."""
        return DownloadService()
    
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
    
    def test_download_audios(self, download_service: DownloadService, 
                            mock_reciters_db, temp_dir: Path):
        """Test downloading audio files."""
        surahs_list = ["audios/alafasy@@1@@1.mp3"]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch('ratteil.services.audio_service.AudioService.get_audio_length') as mock_length:
                mock_length.return_value = 5.0
                
                current_len, max_st = download_service.download_audios(
                    75.0,
                    surahs_list,
                    mock_reciters_db,
                    temp_dir
                )
                
                assert current_len >= 0
                assert isinstance(max_st, bool)


class TestStreamService:
    """Tests for StreamService."""
    
    @pytest.fixture
    def stream_service(self, temp_dir: Path):
        """Create StreamService instance."""
        return StreamService(
            reciters_db={},
            resources_path=temp_dir,
            ratteil_path=temp_dir
        )
    
    def test_prepare_stream_files(self, stream_service: StreamService, temp_dir: Path):
        """Test preparing stream files."""
        # Create test audio files
        audio1 = temp_dir / "audio1.mp3"
        audio2 = temp_dir / "audio2.mp3"
        audio1.write_bytes(b"ID3")
        audio2.write_bytes(b"ID3")
        
        with patch.object(stream_service.audio_service, 'get_audio_length') as mock_length:
            mock_length.side_effect = [5.0, 10.0]  # First file 5 min, second 10 min
            
            stream_service.prepare_stream_files([str(audio1), str(audio2)])
            
            assert len(stream_service.streams) >= 1
    
    def test_generate_stream_details(self, stream_service: StreamService, temp_dir: Path):
        """Test generating stream details."""
        stream_files = [str(temp_dir / "test.mp3")]
        
        with patch('ratteil.services.stream_service.SurahInfo') as mock_surah:
            mock_instance = MagicMock()
            mock_instance.reciter.name = "Test Reciter"
            mock_surah.return_value = mock_instance
            
            with patch('random.choice') as mock_choice:
                mock_choice.return_value = str(temp_dir / "test.mp3")
                
                stream_service.generate_stream_details(stream_files)
                
                assert stream_service.stream_title
                assert stream_service.stream_description


class TestRandomizerService:
    """Tests for RandomizerService."""
    
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
            },
            "husary": {
                "name": "Abdul Basit Abdus Samad",
                "moshaf": [{
                    "moshaf_type": 1,
                    "name": "Murattal",
                    "server": "https://server1.quran.com/husary/",
                    "surah_list": "1,2,3,4,5,6,7,8,9,10"
                }]
            }
        }
    
    def test_get_available_reciters_list(self, mock_reciters_db):
        """Test getting available reciters list."""
        reciters_codes = ["alafasy", "husary"]
        result = RandomizerService.get_available_reciters_list(
            reciters_codes, mock_reciters_db
        )
        
        assert len(result) == 2
        assert all(isinstance(item, str) for item in result)
        assert any("alafasy" in item for item in result)
    
    def test_generate_random_reciters_list(self, mock_reciters_db):
        """Test generating random reciters list."""
        reciters_codes = ["alafasy", "husary"]
        
        with patch('random.choice') as mock_choice:
            mock_choice.side_effect = ["alafasy", "husary"]
            
            result = RandomizerService.generate_random_reciters_list(
                2, reciters_codes, mock_reciters_db
            )
            
            assert len(result) == 2
            assert isinstance(result[0], list)
            assert isinstance(result[1], list)
    
    def test_generate_random_surahs_list(self, mock_reciters_db):
        """Test generating random surahs list."""
        surahs_pool = ["audios/alafasy@@1@@1.mp3", "audios/alafasy@@1@@2.mp3"]
        
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "audios/alafasy@@1@@1.mp3"
            
            result = RandomizerService.generate_random_surahs_list(
                1, None, surahs_pool
            )
            
            assert len(result) == 1
            assert result[0] in surahs_pool


class TestYouTubeService:
    """Tests for YouTubeService."""
    
    @pytest.fixture
    def youtube_service(self):
        """Create YouTubeService instance."""
        with patch.dict(os.environ, {
            "RATTEIL_YOUTUBE_CLIENT_ID": "test_id",
            "RATTEIL_YOUTUBE_CLIENT_SECRET": "test_secret",
        }, clear=True):
            return YouTubeService()
    
    def test_init(self, youtube_service: YouTubeService):
        """Test YouTubeService initialization."""
        assert youtube_service.settings is not None
        assert youtube_service.auth_service is not None


class TestFacebookService:
    """Tests for FacebookService."""
    
    @pytest.fixture
    def facebook_service(self):
        """Create FacebookService instance."""
        with patch.dict(os.environ, {
            "RATTEIL_FACEBOOK_ACCESS_TOKEN": "test_token",
            "RATTEIL_FACEBOOK_APP_SECRET": "test_secret",
        }, clear=True):
            return FacebookService()
    
    def test_init(self, facebook_service: FacebookService):
        """Test FacebookService initialization."""
        assert facebook_service.settings is not None
        assert facebook_service.auth_service is not None
