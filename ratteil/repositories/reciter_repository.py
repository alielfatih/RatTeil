"""Reciter repository for managing reciter data."""

import json
from pathlib import Path
from typing import List, Optional, Protocol

from ratteil.models.reciter import Reciter, Moshaf
from ratteil.config import get_settings


class ReciterRepository(Protocol):
    """Protocol defining the interface for reciter repositories."""
    
    def get_all(self) -> List[Reciter]:
        """Get all reciters."""
        ...
    
    def get_by_id(self, reciter_id: str) -> Optional[Reciter]:
        """Get a reciter by ID."""
        ...
    
    def get_with_multiple_moshafs(self) -> List[Reciter]:
        """Get reciters with multiple moshafs."""
        ...
    
    def get_random(self, count: int = 1) -> List[Reciter]:
        """Get random reciters."""
        ...


class LocalReciterRepository:
    """Local file-based reciter repository."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the repository."""
        settings = get_settings()
        self.data_path = data_path or (settings.DATA_DIR / "reciters.json")
        self._reciters: Optional[List[Reciter]] = None
    
    def _load_reciters(self) -> List[Reciter]:
        """Load reciters from JSON file."""
        if self._reciters is not None:
            return self._reciters
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Reciters data file not found: {self.data_path}")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._reciters = []
        for item in data:
            reciter = Reciter(
                id=item.get('id', ''),
                name=item.get('name', ''),
                bio=item.get('bio'),
                country=item.get('country'),
            )
            
            for moshaf_data in item.get('moshafs', []):
                moshaf = Moshaf(
                    name=moshaf_data.get('name', ''),
                    url=moshaf_data.get('url', ''),
                    description=moshaf_data.get('description'),
                )
                reciter.add_moshaf(moshaf)
            
            self._reciters.append(reciter)
        
        return self._reciters
    
    def get_all(self) -> List[Reciter]:
        """Get all reciters."""
        return self._load_reciters()
    
    def get_by_id(self, reciter_id: str) -> Optional[Reciter]:
        """Get a reciter by ID."""
        for reciter in self._load_reciters():
            if reciter.id == reciter_id:
                return reciter
        return None
    
    def get_with_multiple_moshafs(self) -> List[Reciter]:
        """Get reciters with multiple moshafs."""
        return [r for r in self._load_reciters() if r.has_multiple_moshafs()]
    
    def get_random(self, count: int = 1) -> List[Reciter]:
        """Get random reciters."""
        import random
        reciters = self._load_reciters()
        return random.sample(reciters, min(count, len(reciters)))
    
    def save(self, reciters: List[Reciter]) -> None:
        """Save reciters to JSON file."""
        data = [reciter.to_dict() for reciter in reciters]
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._reciters = None  # Invalidate cache
