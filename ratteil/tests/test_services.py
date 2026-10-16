"""Tests for RatTeil services."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ratteil.services import (
    AudioService,
    DownloadService,
    StreamService,
    RandomizerService,
)
from ratteil.models import Surah, Reciter, Moshaf, StreamDetails, StreamFile
from ratteil.config import DownloadError, AudioMergeError


class TestAudioService:
    """Tests for AudioService."""
    
    @pytest.fixture
    def audio_service(self):
        return AudioService()
    
    def test_get_duration(self, audio_service, tmp_path):
        """Test getting duration of audio file."""
        # Create a dummy audio file (this would need actual audio in real tests)
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        
        # Mock ffprobe
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout="120.5\n",
                stderr="",
                returncode=0,
            )
            
            duration = audio_service.get_duration(audio_file)
            assert duration == 120.5
    
    def test_merge_audios(self, audio_service, tmp_path):
        """Test merging audio files."""
        input_file1 = tmp_path / "input1.mp3"
        input_file2 = tmp_path / "input2.mp3"
        output_file = tmp_path / "output.mp3"
        
        input_file1.touch()
        input_file2.touch()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout="",
                stderr="",
                returncode=0,
            )
            
            result = audio_service.merge_audios(
                [input_file1, input_file2],
                output_file,
            )
            
            assert result == output_file
    
    def test_merge_audios_empty_list(self, audio_service, tmp_path):
        """Test merging with empty list raises error."""
        output_file = tmp_path / "output.mp3"
        
        with pytest.raises(AudioMergeError):
            audio_service.merge_audios([], output_file)
    
    def test_prepare_stream_files(self, audio_service, tmp_path):
        """Test preparing stream files."""
        audio_file = tmp_path / "001_Al-Fatiha_alafasy.mp3"
        audio_file.touch()
        
        with patch.object(audio_service, 'get_duration', return_value=120.5):
            stream_files = audio_service.prepare_stream_files([audio_file])
            
            assert len(stream_files) == 1
            assert stream_files[0].surah_id == 1


class TestDownloadService:
    """Tests for DownloadService."""
    
    @pytest.fixture
    def download_service(self):
        return DownloadService()
    
    def test_download(self, download_service, tmp_path):
        """Test downloading a file."""
        output_file = tmp_path / "test.mp3"
        
        with patch.object(
            download_service.session,
            'get',
            return_value=Mock(
                status_code=200,
                iter_content=[b'test data'],
                raise_for_status=Mock(),
            ),
        ):
            result = download_service.download(
                "https://example.com/test.mp3",
                output_file,
            )
            
            assert result == output_file
            assert output_file.exists()
    
    def test_download_failure(self, download_service, tmp_path):
        """Test download failure raises error."""
        output_file = tmp_path / "test.mp3"
        
        with patch.object(
            download_service.session,
            'get',
            side_effect=Exception("Download failed"),
        ):
            with pytest.raises(DownloadError):
                download_service.download(
                    "https://example.com/test.mp3",
                    output_file,
                )


class TestStreamService:
    """Tests for StreamService."""
    
    @pytest.fixture
    def stream_service(self):
        return StreamService()
    
    @pytest.fixture
    def sample_surahs(self):
        return [
            Surah(
                id=1,
                name="Al-Fatiha",
                arabic_name="الفاتحة",
                translation="The Opening",
                revelation_type="Meccan",
                verses_count=7,
                pages=[1],
            ),
            Surah(
                id=2,
                name="Al-Baqarah",
                arabic_name="البقرة",
                translation="The Cow",
                revelation_type="Medinan",
                verses_count=286,
                pages=[2, 3, 4],
            ),
        ]
    
    @pytest.fixture
    def sample_reciters(self):
        reciter = Reciter(
            id="alafasy",
            name="Mishary Rashid Alafasy",
        )
        reciter.add_moshaf(Moshaf(
            name="Hafs",
            url="https://example.com/{surah_id}.mp3",
        ))
        return [reciter]
    
    def test_generate_stream_details(
        self, stream_service, sample_surahs, sample_reciters, tmp_path
    ):
        """Test generating stream details."""
        # Create dummy audio files
        for surah in sample_surahs:
            for reciter in sample_reciters:
                audio_file = tmp_path / f"{surah.id:03d}_{surah.name.replace(' ', '_')}_{reciter.id}.mp3"
                audio_file.touch()
        
        with patch.object(stream_service.audio_service, 'get_duration', return_value=120.5):
            stream_details = stream_service.generate_stream_details(
                sample_surahs,
                sample_reciters,
                title="Test Stream",
                description="Test Description",
            )
            
            assert stream_details.title == "Test Stream"
            assert stream_details.description == "Test Description"
            assert len(stream_details.stream_files) > 0
    
    def test_stream_validation(self, stream_service, tmp_path):
        """Test stream validation."""
        # Create a valid stream
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        
        stream_details = StreamDetails(
            title="Test Stream",
            description="Test Description",
        )
        
        stream_file = StreamFile(
            path=str(audio_file),
            surah_id=1,
            reciter_id="alafasy",
            duration=120.5,
        )
        stream_details.add_file(stream_file)
        
        assert stream_service.stream_validation(stream_details) is True
    
    def test_stream_validation_no_files(self, stream_service):
        """Test validation fails with no files."""
        stream_details = StreamDetails(
            title="Test Stream",
            description="Test Description",
        )
        
        with pytest.raises(Exception):
            stream_service.stream_validation(stream_details)


class TestRandomizerService:
    """Tests for RandomizerService."""
    
    @pytest.fixture
    def randomizer_service(self, tmp_path):
        # Create test data files
        surahs_data = [
            {
                "id": 1,
                "name": "Al-Fatiha",
                "arabic_name": "الفاتحة",
                "translation": "The Opening",
                "revelation_type": "Meccan",
                "verses_count": 7,
                "pages": [1],
            },
            {
                "id": 2,
                "name": "Al-Baqarah",
                "arabic_name": "البقرة",
                "translation": "The Cow",
                "revelation_type": "Medinan",
                "verses_count": 286,
                "pages": [2, 3, 4],
            },
        ]
        
        reciters_data = [
            {
                "id": "alafasy",
                "name": "Mishary Rashid Alafasy",
                "moshafs": [
                    {"name": "Hafs", "url": "url1"},
                    {"name": "Warsh", "url": "url2"},
                ],
            },
            {
                "id": "husary",
                "name": "Mahmoud Khalil Al-Hussary",
                "moshafs": [
                    {"name": "Hafs", "url": "url1"},
                ],
            },
        ]
        
        # Write test data
        surahs_file = tmp_path / "surahs.json"
        with open(surahs_file, 'w') as f:
            import json
            json.dump(surahs_data, f)
        
        reciters_file = tmp_path / "reciters.json"
        with open(reciters_file, 'w') as f:
            json.dump(reciters_data, f)
        
        # Patch settings to use temp directory
        with patch('ratteil.config.get_settings') as mock_settings:
            from ratteil.config import Settings
            mock_settings.return_value = Settings(
                DATA_DIR=tmp_path,
            )
            
            service = RandomizerService()
            yield service
    
    def test_generate_random_surahs_list(self, randomizer_service):
        """Test generating random surahs list."""
        surahs = randomizer_service.generate_random_surahs_list(count=2)
        
        assert len(surahs) == 2
        assert all(isinstance(s, Surah) for s in surahs)
    
    def test_generate_random_reciters_list(self, randomizer_service):
        """Test generating random reciters list."""
        reciters = randomizer_service.generate_random_reciters_list(count=2)
        
        assert len(reciters) == 2
        assert all(isinstance(r, Reciter) for r in reciters)
    
    def test_get_reciters_with_multi_moshafs(self, randomizer_service):
        """Test getting reciters with multiple moshafs."""
        reciters = randomizer_service.get_reciters_with_multi_moshafs()
        
        assert len(reciters) > 0
        assert all(r.has_multiple_moshafs() for r in reciters)
