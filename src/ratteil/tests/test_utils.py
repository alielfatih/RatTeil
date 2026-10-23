"""
Tests for utilities module.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ratteil.utils.file_utils import surah_index_to_filename, filename_resolve
from ratteil.utils.platform import (
    get_platform,
    is_linux,
    is_windows,
    is_mac,
    is_android,
    is_ios,
    get_ffmpeg_path,
    get_ffprobe_path,
    verify_ffmpeg,
    verify_ffprobe,
    run_command,
    get_temp_dir,
    get_cache_dir,
    get_data_dir,
    get_path_separator,
    normalize_path,
    join_path,
    get_executable_suffix,
    which,
    get_user_home,
    expand_user,
    is_path_absolute,
    get_file_extension,
    change_file_extension,
)


class TestFileUtils:
    """Tests for file utilities."""
    
    def test_surah_index_to_filename_single_digit(self):
        """Test surah index to filename for single digit."""
        assert surah_index_to_filename(1) == "001.mp3"
        assert surah_index_to_filename(5) == "005.mp3"
        assert surah_index_to_filename(9) == "009.mp3"
    
    def test_surah_index_to_filename_double_digit(self):
        """Test surah index to filename for double digit."""
        assert surah_index_to_filename(10) == "010.mp3"
        assert surah_index_to_filename(50) == "050.mp3"
        assert surah_index_to_filename(99) == "099.mp3"
    
    def test_surah_index_to_filename_triple_digit(self):
        """Test surah index to filename for triple digit."""
        assert surah_index_to_filename(100) == "100.mp3"
        assert surah_index_to_filename(114) == "114.mp3"
    
    def test_surah_index_to_filename_invalid(self):
        """Test surah index to filename with invalid index."""
        with pytest.raises(ValueError):
            surah_index_to_filename(0)
        
        with pytest.raises(ValueError):
            surah_index_to_filename(115)
        
        with pytest.raises(ValueError):
            surah_index_to_filename(-1)
    
    def test_filename_resolve(self):
        """Test filename resolution."""
        # Test with full path
        filename = "audios/alafasy@@1@@001.mp3"
        result = filename_resolve(filename)
        assert result == ["001", "alafasy", "1"]
        
        # Test with just filename
        filename = "alafasy@@1@@001.mp3"
        result = filename_resolve(filename)
        assert result == ["001", "alafasy", "1"]


class TestPlatform:
    """Tests for platform utilities."""
    
    def test_get_platform(self):
        """Test platform detection."""
        plat = get_platform()
        assert plat in ["linux", "windows", "darwin", "android", "ios"]
    
    def test_platform_checks(self):
        """Test platform check functions."""
        plat = get_platform()
        
        if plat == "linux":
            assert is_linux() is True
            assert is_windows() is False
            assert is_mac() is False
            assert is_android() is False
            assert is_ios() is False
        elif plat == "windows":
            assert is_windows() is True
            assert is_linux() is False
        elif plat == "darwin":
            assert is_mac() is True
            assert is_linux() is False
    
    def test_get_ffmpeg_path(self):
        """Test FFmpeg path detection."""
        ffmpeg_path = get_ffmpeg_path()
        assert isinstance(ffmpeg_path, str)
        assert len(ffmpeg_path) > 0
    
    def test_get_ffprobe_path(self):
        """Test FFprobe path detection."""
        ffprobe_path = get_ffprobe_path()
        assert isinstance(ffprobe_path, str)
        assert len(ffprobe_path) > 0
    
    def test_get_path_separator(self):
        """Test path separator."""
        sep = get_path_separator()
        assert sep in ["\\", "/"]
    
    def test_normalize_path(self):
        """Test path normalization."""
        path = "test/../test/file.txt"
        normalized = normalize_path(path)
        assert ".." not in normalized
    
    def test_join_path(self):
        """Test path joining."""
        path = join_path("test", "subdir", "file.txt")
        assert isinstance(path, str)
        assert "test" in path
        assert "subdir" in path
        assert "file.txt" in path
    
    def test_get_executable_suffix(self):
        """Test executable suffix."""
        suffix = get_executable_suffix()
        assert suffix in [".exe", ""]
    
    def test_get_user_home(self):
        """Test home directory detection."""
        home = get_user_home()
        assert isinstance(home, Path)
        assert home.exists()
    
    def test_expand_user(self):
        """Test user path expansion."""
        expanded = expand_user("~/test")
        assert isinstance(expanded, str)
        assert "~" not in expanded
    
    def test_is_path_absolute(self):
        """Test absolute path check."""
        assert is_path_absolute("/test") is True
        assert is_path_absolute("test") is False
    
    def test_get_file_extension(self):
        """Test file extension extraction."""
        assert get_file_extension("test.mp3") == ".mp3"
        assert get_file_extension("test.txt") == ".txt"
        assert get_file_extension("test") == ""
    
    def test_change_file_extension(self):
        """Test file extension change."""
        assert change_file_extension("test.mp3", ".wav") == "test.wav"
        assert change_file_extension("test.mp3", "wav") == "test.wav"
        assert change_file_extension("test.txt", ".mp3") == "test.mp3"
    
    def test_get_temp_dir(self):
        """Test temporary directory detection."""
        temp_dir = get_temp_dir()
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
    
    def test_get_cache_dir(self):
        """Test cache directory detection."""
        cache_dir = get_cache_dir()
        assert isinstance(cache_dir, Path)
        # Cache dir may not exist yet
    
    def test_get_data_dir(self):
        """Test data directory detection."""
        data_dir = get_data_dir()
        assert isinstance(data_dir, Path)


class TestWhich:
    """Tests for which function."""
    
    def test_which_existing(self):
        """Test finding existing executable."""
        # Try to find python
        python_path = which("python") or which("python3")
        if python_path:
            assert isinstance(python_path, str)
            assert len(python_path) > 0
    
    def test_which_nonexistent(self):
        """Test finding non-existent executable."""
        result = which("nonexistent_executable_xyz")
        assert result is None
