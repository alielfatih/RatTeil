"""Tests for RatTeil utility functions."""

import pytest
from pathlib import Path

from ratteil.utils import (
    ensure_directory,
    cleanup_files,
    find_audio_files,
    filename_resolve,
    surah_index_to_filename,
    validate_audio_file,
    validate_surah_id,
    validate_reciter_id,
    validate_url,
)
from ratteil.config import ValidationError


class TestFileUtils:
    """Tests for file utility functions."""
    
    def test_ensure_directory(self, tmp_path):
        """Test ensuring a directory exists."""
        new_dir = tmp_path / "new_dir" / "nested"
        
        result = ensure_directory(new_dir)
        
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_cleanup_files(self, tmp_path):
        """Test cleaning up old files."""
        # Create test files
        for i in range(5):
            (tmp_path / f"file{i}.mp3").touch()
        
        # Clean up, keep only 2 latest
        deleted = cleanup_files(tmp_path, pattern="*.mp3", keep_latest=2)
        
        assert deleted == 3
        assert len(list(tmp_path.glob("*.mp3"))) == 2
    
    def test_find_audio_files(self, tmp_path):
        """Test finding audio files."""
        # Create test files
        (tmp_path / "audio1.mp3").touch()
        (tmp_path / "audio2.wav").touch()
        (tmp_path / "not_audio.txt").touch()
        
        files = find_audio_files(tmp_path)
        
        assert len(files) == 2
        assert all(f.suffix in ['.mp3', '.wav'] for f in files)
    
    def test_find_audio_files_with_filters(self, tmp_path):
        """Test finding audio files with filters."""
        # Create test files
        (tmp_path / "001_Surah1_alafasy.mp3").touch()
        (tmp_path / "002_Surah2_alafasy.mp3").touch()
        (tmp_path / "001_Surah1_husary.mp3").touch()
        
        # Filter by reciter
        files = find_audio_files(tmp_path, reciter_id="alafasy")
        assert len(files) == 2
        
        # Filter by surah
        files = find_audio_files(tmp_path, surah_id=1)
        assert len(files) == 2
    
    def test_filename_resolve(self):
        """Test filename resolution."""
        assert filename_resolve("test.mp3") == "test.mp3"
        assert filename_resolve("test file.mp3") == "test_file.mp3"
        assert filename_resolve("test/file.mp3") == "test/file.mp3"
        assert "@" not in filename_resolve("test@file.mp3")
    
    def test_surah_index_to_filename(self, tmp_path, monkeypatch):
        """Test surah index to filename conversion."""
        # Mock the surah repository
        from unittest.mock import Mock
        mock_surah = Mock()
        mock_surah.name = "Al-Fatiha"
        
        with patch('ratteil.repositories.LocalSurahRepository') as mock_repo:
            mock_repo.return_value.get_by_id.return_value = mock_surah
            
            filename = surah_index_to_filename(1, "alafasy")
            assert filename == "001_Al-Fatiha_alafasy.mp3"


class TestValidation:
    """Tests for validation functions."""
    
    def test_validate_audio_file(self, tmp_path):
        """Test audio file validation."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b'dummy audio data')
        
        assert validate_audio_file(audio_file) is True
    
    def test_validate_audio_file_not_exists(self, tmp_path):
        """Test validation fails for non-existent file."""
        audio_file = tmp_path / "nonexistent.mp3"
        
        with pytest.raises(ValidationError):
            validate_audio_file(audio_file)
    
    def test_validate_audio_file_empty(self, tmp_path):
        """Test validation fails for empty file."""
        audio_file = tmp_path / "empty.mp3"
        audio_file.touch()
        
        with pytest.raises(ValidationError):
            validate_audio_file(audio_file)
    
    def test_validate_audio_file_invalid_extension(self, tmp_path):
        """Test validation fails for invalid extension."""
        audio_file = tmp_path / "test.txt"
        audio_file.write_bytes(b'data')
        
        with pytest.raises(ValidationError):
            validate_audio_file(audio_file)
    
    def test_validate_surah_id(self):
        """Test surah ID validation."""
        assert validate_surah_id(1) is True
        assert validate_surah_id(114) is True
        assert validate_surah_id(50) is True
    
    def test_validate_surah_id_invalid(self):
        """Test validation fails for invalid surah ID."""
        with pytest.raises(ValidationError):
            validate_surah_id(0)
        
        with pytest.raises(ValidationError):
            validate_surah_id(115)
        
        with pytest.raises(ValidationError):
            validate_surah_id("invalid")
    
    def test_validate_reciter_id(self):
        """Test reciter ID validation."""
        assert validate_reciter_id("alafasy") is True
        assert validate_reciter_id("husary") is True
        assert validate_reciter_id("test-123") is True
    
    def test_validate_reciter_id_invalid(self):
        """Test validation fails for invalid reciter ID."""
        with pytest.raises(ValidationError):
            validate_reciter_id("")
        
        with pytest.raises(ValidationError):
            validate_reciter_id("test@invalid")
    
    def test_validate_url(self):
        """Test URL validation."""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com/path?query=value") is True
    
    def test_validate_url_invalid(self):
        """Test validation fails for invalid URL."""
        with pytest.raises(ValidationError):
            validate_url("")
        
        with pytest.raises(ValidationError):
            validate_url("not a url")
        
        with pytest.raises(ValidationError):
            validate_url("ftp://example.com")
