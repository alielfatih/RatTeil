"""File utility functions."""

import glob
import os
import re
from pathlib import Path
from typing import List, Optional, Union

from ratteil.config import get_settings


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def cleanup_files(
    directory: Union[str, Path],
    pattern: str = "*.mp3",
    keep_latest: int = 10,
) -> int:
    """Clean up old files in a directory.
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match
        keep_latest: Number of latest files to keep
        
    Returns:
        Number of files deleted
    """
    directory = Path(directory)
    if not directory.exists():
        return 0
    
    files = list(directory.glob(pattern))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    deleted_count = 0
    for file_path in files[keep_latest:]:
        file_path.unlink()
        deleted_count += 1
    
    return deleted_count


def find_audio_files(
    directory: Union[str, Path],
    reciter_id: Optional[str] = None,
    surah_id: Optional[int] = None,
) -> List[Path]:
    """Find audio files matching criteria.
    
    Args:
        directory: Directory to search
        reciter_id: Optional reciter ID filter
        surah_id: Optional surah ID filter
        
    Returns:
        List of matching audio file paths
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    
    files = list(directory.rglob("*.mp3"))
    
    if reciter_id:
        files = [f for f in files if reciter_id in f.stem]
    
    if surah_id is not None:
        files = [f for f in files if f"{surah_id:03d}" in f.stem]
    
    return files


def filename_resolve(filename: str) -> str:
    """Resolve a filename to a standardized format.
    
    Args:
        filename: Input filename
        
    Returns:
        Standardized filename
    """
    # Remove special characters and normalize
    filename = re.sub(r'[^\w\-.]', '_', filename)
    return filename


def surah_index_to_filename(surah_index: int, reciter_id: str = "") -> str:
    """Convert a surah index to a standardized filename.
    
    Args:
        surah_index: Surah index (1-114)
        reciter_id: Optional reciter ID to include in filename
        
    Returns:
        Standardized filename
    """
    settings = get_settings()
    
    # Load surah list to get the name
    from ratteil.repositories.surah_repository import LocalSurahRepository
    repo = LocalSurahRepository()
    
    try:
        surah = repo.get_by_id(surah_index)
        if surah:
            name = surah.name.replace(' ', '_')
        else:
            name = f"Surah_{surah_index}"
    except Exception:
        name = f"Surah_{surah_index}"
    
    if reciter_id:
        return f"{surah_index:03d}_{name}_{reciter_id}.{settings.AUDIO_FORMAT}"
    
    return f"{surah_index:03d}_{name}.{settings.AUDIO_FORMAT}"
