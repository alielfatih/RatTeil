"""Surah repository for managing surah data."""

import json
from pathlib import Path
from typing import List, Optional, Protocol

from ratteil.models.surah import Surah
from ratteil.config import get_settings


class SurahRepository(Protocol):
    """Protocol defining the interface for surah repositories."""
    
    def get_all(self) -> List[Surah]:
        """Get all surahs."""
        ...
    
    def get_by_id(self, surah_id: int) -> Optional[Surah]:
        """Get a surah by ID."""
        ...
    
    def get_random(self, count: int = 1) -> List[Surah]:
        """Get random surahs."""
        ...


class LocalSurahRepository:
    """Local file-based surah repository."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the repository."""
        settings = get_settings()
        self.data_path = data_path or (settings.DATA_DIR / "surahs.json")
        self._surahs: Optional[List[Surah]] = None
    
    def _load_surahs(self) -> List[Surah]:
        """Load surahs from JSON file."""
        if self._surahs is not None:
            return self._surahs
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Surahs data file not found: {self.data_path}")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._surahs = []
        for item in data:
            surah = Surah(
                id=item.get('id', 0),
                name=item.get('name', ''),
                arabic_name=item.get('arabic_name', ''),
                translation=item.get('translation', ''),
                revelation_type=item.get('revelation_type', 'Unknown'),
                verses_count=item.get('verses_count', 0),
                pages=item.get('pages', []),
            )
            self._surahs.append(surah)
        
        return self._surahs
    
    def get_all(self) -> List[Surah]:
        """Get all surahs."""
        return self._load_surahs()
    
    def get_by_id(self, surah_id: int) -> Optional[Surah]:
        """Get a surah by ID."""
        for surah in self._load_surahs():
            if surah.id == surah_id:
                return surah
        return None
    
    def get_random(self, count: int = 1) -> List[Surah]:
        """Get random surahs."""
        import random
        surahs = self._load_surahs()
        return random.sample(surahs, min(count, len(surahs)))
    
    def save(self, surahs: List[Surah]) -> None:
        """Save surahs to JSON file."""
        data = []
        for surah in surahs:
            data.append({
                "id": surah.id,
                "name": surah.name,
                "arabic_name": surah.arabic_name,
                "translation": surah.translation,
                "revelation_type": surah.revelation_type,
                "verses_count": surah.verses_count,
                "pages": surah.pages,
            })
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._surahs = None  # Invalidate cache
