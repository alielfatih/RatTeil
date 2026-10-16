"""Stream model definitions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class StreamStatus(Enum):
    """Status of a stream."""
    PENDING = "pending"
    PREPARING = "preparing"
    LIVE = "live"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class StreamFile:
    """Represents a file prepared for streaming."""
    
    path: str
    surah_id: int
    reciter_id: str
    duration: float
    order: int = 0
    
    def __str__(self) -> str:
        return f"StreamFile(path='{self.path}', surah={self.surah_id}, reciter={self.reciter_id})"


@dataclass
class StreamDetails:
    """Details about a stream."""
    
    title: str
    description: str
    stream_files: List[StreamFile] = field(default_factory=list)
    total_duration: float = 0.0
    status: StreamStatus = StreamStatus.PENDING
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    stream_url: Optional[str] = None
    broadcast_id: Optional[str] = None
    stream_id: Optional[str] = None
    
    def add_file(self, stream_file: StreamFile) -> None:
        """Add a file to the stream."""
        self.stream_files.append(stream_file)
        self.total_duration += stream_file.duration
        # Sort by order
        self.stream_files.sort(key=lambda x: x.order)
    
    def get_next_file(self) -> Optional[StreamFile]:
        """Get the next file to stream (FIFO)."""
        if self.stream_files:
            return self.stream_files.pop(0)
        return None
    
    def mark_live(self) -> None:
        """Mark the stream as live."""
        self.status = StreamStatus.LIVE
        self.actual_start = datetime.now()
    
    def mark_completed(self) -> None:
        """Mark the stream as completed."""
        self.status = StreamStatus.COMPLETED
    
    def mark_error(self) -> None:
        """Mark the stream as error."""
        self.status = StreamStatus.ERROR
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "description": self.description,
            "total_duration": self.total_duration,
            "status": self.status.value,
            "scheduled_start": self.scheduled_start.isoformat() if self.scheduled_start else None,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "stream_url": self.stream_url,
            "broadcast_id": self.broadcast_id,
            "stream_id": self.stream_id,
            "files": [
                {
                    "path": f.path,
                    "surah_id": f.surah_id,
                    "reciter_id": f.reciter_id,
                    "duration": f.duration,
                    "order": f.order,
                }
                for f in self.stream_files
            ],
        }
    
    def __str__(self) -> str:
        return f"StreamDetails(title='{self.title}', status={self.status.value}, files={len(self.stream_files)})"
