"""
Platform compatibility utilities for RatTeil application.

This module provides cross-platform support for:
- Path handling
- FFmpeg detection and execution
- Shell command execution
- Platform detection
"""

import os
import sys
import subprocess
import platform as plt
from pathlib import Path
from typing import List, Optional, Tuple

from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import FileError
from ratteil.utils.logging import get_logger


logger = get_logger("ratteil.utils.platform")


def get_platform() -> str:
    """
    Get the current platform.
    
    Returns:
        Platform name: 'linux', 'windows', 'darwin', 'android', or 'ios'
    """
    system = plt.system().lower()
    
    if system == "linux":
        # Check for Android (Termux)
        if "ANDROID_ROOT" in os.environ or "PREFIX" in os.environ:
            return "android"
        return "linux"
    elif system == "windows":
        return "windows"
    elif system == "darwin":
        return "darwin"
    else:
        return system


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform() == "linux"


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform() == "windows"


def is_mac() -> bool:
    """Check if running on macOS."""
    return get_platform() == "darwin"


def is_android() -> bool:
    """Check if running on Android (Termux)."""
    return get_platform() == "android"


def is_ios() -> bool:
    """Check if running on iOS."""
    return get_platform() == "ios"


def get_ffmpeg_path() -> str:
    """
    Get the path to FFmpeg executable.
    
    Returns:
        Path to FFmpeg executable
    """
    settings = get_settings()
    
    # Check if custom path is configured
    if settings.ffmpeg_path and Path(settings.ffmpeg_path).exists():
        return str(settings.ffmpeg_path)
    
    # Platform-specific paths
    plat = get_platform()
    
    if plat == "windows":
        # Try common Windows locations
        possible_paths = [
            "ffmpeg.exe",
            Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
        ]
    elif plat == "android":
        # Termux path
        possible_paths = [
            "/data/data/com.termux/files/usr/bin/ffmpeg",
            "ffmpeg",
        ]
    else:
        # Linux/Mac
        possible_paths = [
            "ffmpeg",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            Path.home() / ".local" / "bin" / "ffmpeg",
        ]
    
    # Check each possible path
    for path in possible_paths:
        if Path(path).exists():
            return str(path)
    
    # Return default
    return "ffmpeg"


def get_ffprobe_path() -> str:
    """
    Get the path to FFprobe executable.
    
    Returns:
        Path to FFprobe executable
    """
    settings = get_settings()
    
    # Check if custom path is configured
    if settings.ffprobe_path and Path(settings.ffprobe_path).exists():
        return str(settings.ffprobe_path)
    
    # Use same logic as FFmpeg but with ffprobe
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path.endswith(".exe"):
        return ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
    return ffmpeg_path.replace("ffmpeg", "ffprobe")


def verify_ffmpeg() -> bool:
    """
    Verify that FFmpeg is available and working.
    
    Returns:
        True if FFmpeg is available, False otherwise
    """
    try:
        ffmpeg_path = get_ffmpeg_path()
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"FFmpeg verification failed: {e}")
        return False


def verify_ffprobe() -> bool:
    """
    Verify that FFprobe is available and working.
    
    Returns:
        True if FFprobe is available, False otherwise
    """
    try:
        ffprobe_path = get_ffprobe_path()
        result = subprocess.run(
            [ffprobe_path, "-version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"FFprobe verification failed: {e}")
        return False


def get_shell_command(cmd: str) -> str:
    """
    Get the shell command for the current platform.
    
    Args:
        cmd: Command to execute
        
    Returns:
        Platform-appropriate shell command
    """
    plat = get_platform()
    
    if plat == "windows":
        return f'"{cmd}"'
    else:
        return cmd


def run_command(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Run a command with platform-specific handling.
    
    Args:
        cmd: Command and arguments as list
        **kwargs: Additional arguments for subprocess.run
        
    Returns:
        CompletedProcess result
    """
    plat = get_platform()
    
    # On Windows, use shell=True for better compatibility
    if plat == "windows":
        kwargs.setdefault("shell", True)
        # Convert list to string for Windows
        cmd_str = " ".join(cmd)
        return subprocess.run(cmd_str, **kwargs)
    
    return subprocess.run(cmd, **kwargs)


def get_temp_dir() -> Path:
    """
    Get the appropriate temporary directory for the platform.
    
    Returns:
        Path to temporary directory
    """
    plat = get_platform()
    
    if plat == "android":
        # Use Termux temporary directory
        temp_dir = Path("/data/data/com.termux/files/usr/tmp")
        if temp_dir.exists():
            return temp_dir
    
    # Use standard temp directory
    return Path(tempfile.gettempdir())


def get_cache_dir() -> Path:
    """
    Get the appropriate cache directory for the platform.
    
    Returns:
        Path to cache directory
    """
    plat = get_platform()
    
    if plat == "windows":
        # Windows cache directory
        local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        cache_dir = local_app_data / "RatTeil" / "cache"
    elif plat == "android":
        # Android cache directory
        cache_dir = Path("/data/data/com.termux/files/home/.cache/RatTeil")
    else:
        # Linux/Mac cache directory
        cache_dir = Path.home() / ".cache" / "RatTeil"
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_data_dir() -> Path:
    """
    Get the appropriate data directory for the platform.
    
    Returns:
        Path to data directory
    """
    settings = get_settings()
    return settings.data_dir


def get_path_separator() -> str:
    """
    Get the path separator for the current platform.
    
    Returns:
        Path separator character
    """
    return os.sep


def normalize_path(path: str) -> str:
    """
    Normalize a path for the current platform.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path
    """
    return os.path.normpath(path)


def join_path(*parts: str) -> str:
    """
    Join path parts using the platform-specific separator.
    
    Args:
        *parts: Path parts to join
        
    Returns:
        Joined path
    """
    return os.path.join(*parts)


def get_executable_suffix() -> str:
    """
    Get the executable suffix for the current platform.
    
    Returns:
        Executable suffix (e.g., '.exe' on Windows, '' on others)
    """
    if is_windows():
        return ".exe"
    return ""


def which(executable: str) -> Optional[str]:
    """
    Find the full path to an executable.
    
    Args:
        executable: Executable name
        
    Returns:
        Full path to executable, or None if not found
    """
    plat = get_platform()
    
    if plat == "windows":
        # Try with .exe suffix
        exe_name = executable + ".exe"
        for path in os.environ.get("PATH", "").split(os.pathsep):
            full_path = Path(path) / exe_name
            if full_path.exists():
                return str(full_path)
        
        # Try without .exe
        for path in os.environ.get("PATH", "").split(os.pathsep):
            full_path = Path(path) / executable
            if full_path.exists():
                return str(full_path)
    else:
        # Use which command on Unix-like systems
        try:
            import shutil
            return shutil.which(executable)
        except AttributeError:
            # Fallback for systems without shutil.which
            for path in os.environ.get("PATH", "").split(os.pathsep):
                full_path = Path(path) / executable
                if full_path.exists():
                    return str(full_path)
    
    return None


def get_user_home() -> Path:
    """
    Get the user's home directory.
    
    Returns:
        Path to home directory
    """
    return Path.home()


def expand_user(path: str) -> str:
    """
    Expand ~ in path to user's home directory.
    
    Args:
        path: Path to expand
        
    Returns:
        Expanded path
    """
    return os.path.expanduser(path)


def is_path_absolute(path: str) -> bool:
    """
    Check if a path is absolute.
    
    Args:
        path: Path to check
        
    Returns:
        True if path is absolute
    """
    return os.path.isabs(path)


def get_file_extension(path: str) -> str:
    """
    Get the file extension from a path.
    
    Args:
        path: File path
        
    Returns:
        File extension
    """
    return os.path.splitext(path)[1]


def change_file_extension(path: str, new_ext: str) -> str:
    """
    Change the file extension of a path.
    
    Args:
        path: Original path
        new_ext: New extension (with or without dot)
        
    Returns:
        Path with new extension
    """
    if not new_ext.startswith("."):
        new_ext = "." + new_ext
    return os.path.splitext(path)[0] + new_ext
