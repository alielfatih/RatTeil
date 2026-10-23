"""
Data models for Quran information in RatTeil application.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime


@dataclass
class Language:
    """
    Represents a language for Quran data.
    
    Attributes:
        code: Language code (e.g., 'ar', 'en', 'fr')
        name: Language name in English
        native_name: Language name in its own script
        rtl: Whether the language is right-to-left
    """
    code: str
    name: str
    native_name: str
    rtl: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "name": self.name,
            "native_name": self.native_name,
            "rtl": self.rtl,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Language":
        """Create from dictionary."""
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            native_name=data.get("native_name", ""),
            rtl=data.get("rtl", False),
        )


@dataclass
class Reciter:
    """
    Represents a Quran reciter.
    
    Attributes:
        id: Unique identifier
        name: Reciter name
        code: Reciter code (e.g., alafasy, husary)
        letter: Starting letter of the name
        moshafs: List of available recordings
        language: Language code for this reciter's data
    """
    id: int
    name: str
    code: str = ""
    letter: str = ""
    moshafs: List[Dict[str, Any]] = field(default_factory=list)
    language: str = "ar"
    
    def get_moshaf_urls(self) -> List[str]:
        """Get all moshaf base URLs."""
        urls = []
        for moshaf in self.moshafs:
            server = moshaf.get("server", "")
            if server:
                # Clean up escaped slashes
                server = server.replace("\\/", "/").replace("\\\\", "")
                urls.append(server)
        return urls
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "letter": self.letter,
            "moshafs": self.moshafs,
            "language": self.language,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], language: str = "ar") -> "Reciter":
        """Create from dictionary."""
        return cls(
            id=data.get("id", 0),
            code=data.get("code", ""),
            name=data.get("name", ""),
            letter=data.get("letter", data.get("name", "")[0] if data.get("name") else ""),
            moshafs=data.get("moshaf", data.get("moshafs", [])),
            language=language,
        )


@dataclass
class Surah:
    """
    Represents a Quran surah.
    
    Attributes:
        id: Surah number (1-114)
        name: Surah name
        arabic_name: Surah name in Arabic
        ayahs: Number of verses
        revelation_place: Where revealed (Makkah or Madinah)
        language: Language code for this surah's data
    """
    id: int
    name: str
    arabic_name: str = ""
    ayahs: int = 0
    revelation_place: str = ""
    language: str = "ar"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "arabic_name": self.arabic_name,
            "ayahs": self.ayahs,
            "revelation_place": self.revelation_place,
            "language": self.language,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], language: str = "ar") -> "Surah":
        """Create from dictionary."""
        return cls(
            id=data.get("id", data.get("number", data.get("index", 0))),
            name=data.get("name", data.get("englishName", "")),
            arabic_name=data.get("arabicName", data.get("name", "")),
            ayahs=data.get("ayahs", data.get("numberOfAyahs", 0)),
            revelation_place=data.get("revelationPlace", ""),
            language=language,
        )


@dataclass
class QuranData:
    """
    Container for all Quran data.
    
    Attributes:
        languages: Available languages
        reciters: List of reciters
        surahs: List of surahs
        cached_at: When data was cached
        language: Current language
        version: Data version
    """
    languages: List[Language] = field(default_factory=list)
    reciters: List[Reciter] = field(default_factory=list)
    surahs: List[Surah] = field(default_factory=list)
    cached_at: Optional[datetime] = None
    language: str = "ar"
    version: str = "1.0"
    
    def get_reciter_by_id(self, reciter_id: int) -> Optional[Reciter]:
        """Get reciter by ID."""
        for reciter in self.reciters:
            if reciter.id == reciter_id:
                return reciter
        return None
    
    def get_reciter_by_code(self, code: str) -> Optional[Reciter]:
        """Get reciter by code."""
        for reciter in self.reciters:
            if reciter.code == code.lower():
                return reciter
        return None
    
    def get_surah_by_id(self, surah_id: int) -> Optional[Surah]:
        """Get surah by ID."""
        for surah in self.surahs:
            if surah.id == surah_id:
                return surah
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "languages": [l.to_dict() for l in self.languages],
            "reciters": [r.to_dict() for r in self.reciters],
            "surahs": [s.to_dict() for s in self.surahs],
            "cached_at": self.cached_at.isoformat() if self.cached_at else None,
            "language": self.language,
            "version": self.version,
        }
    
    def save_to_json(self, path: Path) -> None:
        """Save to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, path: Path) -> "QuranData":
        """Load from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        languages = [Language.from_dict(l) for l in data.get("languages", [])]
        reciters = [Reciter.from_dict(r, data.get("language", "ar")) for r in data.get("reciters", [])]
        surahs = [Surah.from_dict(s, data.get("language", "ar")) for s in data.get("surahs", [])]
        
        return cls(
            languages=languages,
            reciters=reciters,
            surahs=surahs,
            cached_at=datetime.fromisoformat(data["cached_at"]) if data.get("cached_at") else None,
            language=data.get("language", "ar"),
            version=data.get("version", "1.0"),
        )
