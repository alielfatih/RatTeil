"""Validation utility functions."""

import re
from pathlib import Path
from typing import List, Optional, Union

from ratteil.config import ValidationError
from ratteil.models.stream import StreamDetails


def validate_audio_file(file_path: Union[str, Path]) -> bool:
    """Validate that a file is a valid audio file.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If file is invalid
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    if file_path.stat().st_size == 0:
        raise ValidationError(f"File is empty: {file_path}")
    
    # Check file extension
    valid_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
    if file_path.suffix.lower() not in valid_extensions:
        raise ValidationError(
            f"Invalid audio file extension: {file_path.suffix}"
        )
    
    return True


def validate_surah_id(surah_id: int) -> bool:
    """Validate a surah ID.
    
    Args:
        surah_id: Surah ID to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If surah ID is invalid
    """
    if not isinstance(surah_id, int):
        raise ValidationError(f"Surah ID must be an integer, got {type(surah_id)}")
    
    if surah_id < 1 or surah_id > 114:
        raise ValidationError(f"Surah ID must be between 1 and 114, got {surah_id}")
    
    return True


def validate_reciter_id(reciter_id: str) -> bool:
    """Validate a reciter ID.
    
    Args:
        reciter_id: Reciter ID to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If reciter ID is invalid
    """
    if not isinstance(reciter_id, str):
        raise ValidationError(
            f"Reciter ID must be a string, got {type(reciter_id)}"
        )
    
    if not reciter_id.strip():
        raise ValidationError("Reciter ID cannot be empty")
    
    # Check for valid characters
    if not re.match(r'^[\w\-]+$', reciter_id):
        raise ValidationError(
            f"Reciter ID contains invalid characters: {reciter_id}"
        )
    
    return True


def validate_stream_details(stream_details: StreamDetails) -> bool:
    """Validate stream details.
    
    Args:
        stream_details: StreamDetails to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If stream details are invalid
    """
    if not stream_details.title:
        raise ValidationError("Stream title cannot be empty")
    
    if not stream_details.stream_files:
        raise ValidationError("Stream must have at least one file")
    
    # Validate all files
    for stream_file in stream_details.stream_files:
        validate_audio_file(stream_file.path)
    
    return True


def validate_url(url: str) -> bool:
    """Validate a URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not isinstance(url, str):
        raise ValidationError(f"URL must be a string, got {type(url)}")
    
    if not url.strip():
        raise ValidationError("URL cannot be empty")
    
    # Simple URL validation
    if not re.match(r'^https?://', url, re.IGNORECASE):
        raise ValidationError(f"Invalid URL format: {url}")
    
    return True
