"""Surah model definitions."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Surah:
    """Represents a Surah (chapter) from the Quran."""
    
    id: int
    name: str
    arabic_name: str
    translation: str
    revelation_type: str  # "Meccan" or "Medinan"
    verses_count: int
    pages: List[int]
    
    @property
    def filename(self) -> str:
        """Generate a standardized filename for the surah."""
        return f"{self.id:03d}_{self.name.replace(' ', '_')}.mp3"
    
    def __str__(self) -> str:
        return f"Surah {self.id}: {self.name} ({self.arabic_name})"
    
    def __repr__(self) -> str:
        return f"Surah(id={self.id}, name='{self.name}')"


@dataclass
class SurahInfo:
    """Information about a surah for display purposes."""
    
    surah: Surah
    reciter: Optional[str] = None
    duration: Optional[float] = None
    file_path: Optional[str] = None
    
    def __str__(self) -> str:
        reciter_str = f" by {self.reciter}" if self.reciter else ""
        duration_str = f" ({self.duration}s)" if self.duration else ""
        return f"{self.surah}{reciter_str}{duration_str}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.surah.id,
            "name": self.surah.name,
            "arabic_name": self.surah.arabic_name,
            "reciter": self.reciter,
            "duration": self.duration,
            "file_path": self.file_path,
        }
