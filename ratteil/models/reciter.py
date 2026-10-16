"""Reciter model definitions."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class MoshafType(Enum):
    """Types of Moshaf (Quran edition)."""
    HAFS = "Hafs"
    WARSH = "Warsh"
    QALUN = "Qalun"
    OTHER = "Other"


@dataclass
class Moshaf:
    """Represents a Moshaf (Quran edition/recitation style)."""
    
    name: str
    url: str
    moshaf_type: MoshafType = MoshafType.OTHER
    description: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.name} ({self.moshaf_type.value})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "url": self.url,
            "type": self.moshaf_type.value,
            "description": self.description,
        }


@dataclass
class Reciter:
    """Represents a Quran reciter."""
    
    id: str
    name: str
    bio: Optional[str] = None
    moshafs: List[Moshaf] = field(default_factory=list)
    country: Optional[str] = None
    
    def __init__(
        self,
        id: str,
        name: str,
        bio: Optional[str] = None,
        moshafs: Optional[List[Moshaf]] = None,
        country: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.bio = bio
        self.moshafs = moshafs or []
        self.country = country
    
    def add_moshaf(self, moshaf: Moshaf) -> None:
        """Add a moshaf to the reciter."""
        self.moshafs.append(moshaf)
    
    def get_moshaf_name_url(self) -> List[tuple]:
        """Get list of (name, url) tuples for all moshafs."""
        return [(m.name, m.url) for m in self.moshafs]
    
    def has_multiple_moshafs(self) -> bool:
        """Check if reciter has multiple moshafs."""
        return len(self.moshafs) > 1
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
    
    def __repr__(self) -> str:
        return f"Reciter(id='{self.id}', name='{self.name}')"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "country": self.country,
            "moshafs": [m.to_dict() for m in self.moshafs],
        }
