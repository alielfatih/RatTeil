"""
Stream models for RatTeil application.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta


@dataclass
class StreamConfig:
    """
    Configuration for a stream.
    
    Attributes:
        title: Stream title
        description: Stream description
        platform: Platform to stream to (youtube, facebook, etc.)
        max_length: Maximum stream length in minutes
        min_length: Minimum stream length in minutes
        reciters: List of reciter codes to use
        surahs: List of surah indices to use
        output_dir: Directory for output files
        fixer_dir: Directory for fixer files (intro/outro)
        img_dir: Directory for images
    """
    title: str = ""
    description: str = ""
    platform: str = "youtube"
    max_length: float = 75.0
    min_length: float = 120.0
    reciters: List[str] = field(default_factory=list)
    surahs: List[int | str] = field(default_factory=list)
    output_dir: Path = field(default=Path("./audios"))
    fixer_dir: Path = field(default=Path("./fixer"))
    img_dir: Path = field(default=Path("./imgs"))
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_length < 1:
            raise ValueError("max_length must be at least 1 minute")
        if self.min_length < 1:
            raise ValueError("min_length must be at least 1 minute")
        if self.platform not in ["youtube", "facebook", "fb", "yt"]:
            raise ValueError(f"Unsupported platform: {self.platform}")


@dataclass
class StreamDetails:
    """
    Details about a stream session.
    
    Attributes:
        stream_id: Unique identifier for the stream
        title: Stream title
        description: Stream description
        platform: Platform being streamed to
        start_time: When the stream started
        end_time: When the stream is scheduled to end
        status: Current status (pending, live, completed, error)
        audio_files: List of audio files in the stream
        total_duration: Total duration of all audio files in minutes
        stream_url: URL where the stream can be viewed
        stream_key: Stream key for RTMP streaming
        error: Any error that occurred
    """
    stream_id: str
    title: str = ""
    description: str = ""
    platform: str = "youtube"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"
    audio_files: List[Path] = field(default_factory=list)
    total_duration: float = 0.0
    stream_url: Optional[str] = None
    stream_key: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.end_time is None:
            self.end_time = self.start_time + timedelta(minutes=75)
    
    def mark_live(self, stream_url: str, stream_key: str) -> None:
        """Mark the stream as live."""
        self.status = "live"
        self.stream_url = stream_url
        self.stream_key = stream_key
    
    def mark_completed(self) -> None:
        """Mark the stream as completed."""
        self.status = "completed"
        self.end_time = datetime.now()
    
    def mark_error(self, error: str) -> None:
        """Mark the stream as error."""
        self.status = "error"
        self.error = error
        self.end_time = datetime.now()
    
    def is_live(self) -> bool:
        """Check if stream is currently live."""
        return self.status == "live"
    
    def is_completed(self) -> bool:
        """Check if stream has completed."""
        return self.status == "completed"
    
    def is_error(self) -> bool:
        """Check if stream encountered an error."""
        return self.status == "error"
    
    def get_remaining_time(self) -> timedelta:
        """Get remaining time for the stream."""
        if self.end_time:
            return self.end_time - datetime.now()
        return timedelta(0)
