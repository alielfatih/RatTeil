"""
Data manager for Quran data in RatTeil application.

Provides unified interface for fetching and caching Quran data
from API or local files.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from ratteil.data.models import Language, Reciter, Surah, QuranData
from ratteil.data.api_client import QuranAPIClient
from ratteil.data.exceptions import DataError, CacheError, LanguageNotSupportedError
from ratteil.config.settings import get_settings
from ratteil.utils.logging import get_logger


class QuranDataManager:
    """
    Manager for Quran data with online/offline modes.
    
    Features:
    - Fetch data from mp3quran.net API
    - Cache data to JSON files
    - Support multiple languages
    - Offline mode with cached data
    - Automatic cache expiration
    """
    
    # Cache expiration time (1 day)
    CACHE_EXPIRY_HOURS = 24
    
    def __init__(self, language: str = "ar", offline: bool = False):
        """
        Initialize data manager.
        
        Args:
            language: Language code (default: 'ar')
            offline: Whether to use offline mode (default: False)
        """
        self.settings = get_settings()
        self.logger = get_logger("ratteil.data.manager")
        self.language = language
        self.offline = offline
        self._data: Optional[QuranData] = None
        
        # Set up cache directory
        self.cache_dir = self.settings.data_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def data(self) -> QuranData:
        """Get cached data, loading if necessary."""
        if self._data is None:
            self._data = self.load_data()
        return self._data
    
    def set_language(self, language: str) -> None:
        """Set the language for data."""
        if language != self.language:
            self.language = language
            self._data = None  # Reset cached data
    
    def set_offline(self, offline: bool) -> None:
        """Set offline mode."""
        self.offline = offline
        if offline:
            self.logger.info(f"Switched to offline mode with language: {self.language}")
        else:
            self.logger.info(f"Switched to online mode with language: {self.language}")
    
    def _get_cache_path(self, data_type: str) -> Path:
        """Get path for cache file."""
        return self.cache_dir / f"{data_type}_{self.language}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid (not expired)."""
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            cached_at_str = data.get("cached_at")
            if not cached_at_str:
                return False
            
            cached_at = datetime.fromisoformat(cached_at_str)
            expiry = cached_at + timedelta(hours=self.CACHE_EXPIRY_HOURS)
            
            return datetime.now() < expiry
        except Exception as e:
            self.logger.warning(f"Failed to check cache validity: {e}")
            return False
    
    def load_data(self, force_refresh: bool = False) -> QuranData:
        """
        Load Quran data.
        
        Args:
            force_refresh: Force refresh from API (ignore cache)
            
        Returns:
            QuranData object
        """
        if self.offline:
            return self._load_from_cache()
        
        # Try to load from cache first
        if not force_refresh:
            try:
                cached_data = self._load_from_cache()
                if cached_data:
                    self.logger.debug(f"Loaded data from cache for language: {self.language}")
                    return cached_data
            except Exception as e:
                self.logger.warning(f"Failed to load from cache: {e}")
        
        # Fetch from API
        self.logger.info(f"Fetching data from API for language: {self.language}")
        client = QuranAPIClient()
        
        try:
            data = client.get_all_data_sync(self.language)
            self._save_to_cache(data)
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch from API: {e}")
            # Fallback to cache or default data
            try:
                return self._load_from_cache()
            except Exception:
                return self._get_default_data()
    
    def _load_from_cache(self) -> QuranData:
        """Load data from cache files."""
        # Load languages
        languages_path = self._get_cache_path("languages")
        languages = self._load_json_file(languages_path, "languages")
        
        # Load reciters
        reciters_path = self._get_cache_path("reciters")
        reciters = self._load_json_file(reciters_path, "reciters")
        
        # Load surahs
        surahs_path = self._get_cache_path("surahs")
        surahs = self._load_json_file(surahs_path, "surahs")
        
        # If no cache files exist, return default data
        if not languages and not reciters and not surahs:
            return self._get_default_data()
        
        return QuranData(
            languages=languages,
            reciters=reciters,
            surahs=surahs,
            cached_at=datetime.now(),
            language=self.language,
            version="1.0"
        )
    
    def _load_json_file(self, path: Path, data_type: str) -> List:
        """Load JSON file and convert to model objects."""
        if not path.exists():
            self.logger.warning(f"Cache file not found: {path}")
            return []
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            items = data.get("items", [])
            
            if data_type == "languages":
                return [Language.from_dict(item) for item in items]
            elif data_type == "reciters":
                return [Reciter.from_dict(item, self.language) for item in items]
            elif data_type == "surahs":
                return [Surah.from_dict(item, self.language) for item in items]
            
            return []
        except Exception as e:
            self.logger.warning(f"Failed to load {data_type} from cache: {e}")
            return []
    
    def _save_to_cache(self, data: QuranData) -> None:
        """Save data to cache files."""
        try:
            # Save languages
            languages_path = self._get_cache_path("languages")
            self._save_json_file(languages_path, "languages", data.languages)
            
            # Save reciters
            reciters_path = self._get_cache_path("reciters")
            self._save_json_file(reciters_path, "reciters", data.reciters)
            
            # Save surahs
            surahs_path = self._get_cache_path("surahs")
            self._save_json_file(surahs_path, "surahs", data.surahs)
            
            self.logger.debug(f"Saved data to cache for language: {self.language}")
        except Exception as e:
            self.logger.error(f"Failed to save to cache: {e}")
            raise CacheError(f"Failed to save cache: {e}") from e
    
    def _save_json_file(self, path: Path, data_type: str, items: List) -> None:
        """Save list of items to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "items": [item.to_dict() for item in items],
            "cached_at": datetime.now().isoformat(),
            "language": self.language,
            "version": "1.0"
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_default_data(self) -> QuranData:
        """Get default data when API and cache fail."""
        self.logger.warning("Using default data (API and cache unavailable)")
        
        # Create default data from existing reciters.py
        try:
            from ratteil.reciters import reciters as reciters_dict, reciters_code
            from ratteil.surahs import surah_list as surahs_dict
            
            # Convert old format to new
            reciters = []
            for code, reciter_data in reciters_dict.items():
                moshafs = reciter_data.get("moshaf", [])
                # Clean up server URLs
                for moshaf in moshafs:
                    if "server" in moshaf:
                        moshaf["server"] = moshaf["server"].replace("\\/", "/").replace("\\\\", "")
                
                reciters.append(Reciter(
                    id=reciter_data.get("id", len(reciters) + 1),
                    name=reciter_data.get("name", code),
                    letter=reciter_data.get("letter", ""),
                    moshafs=moshafs,
                    language="ar"
                ))
            
            # Convert surahs
            surahs = []
            for i in range(1, 115):
                surah_key = f"surah_{i}"
                surah_data = surahs_dict.get(surah_key, {})
                surahs.append(Surah(
                    id=i,
                    name=surah_data.get("name", f"Surah {i}"),
                    arabic_name=surah_data.get("arabic", ""),
                    ayahs=surah_data.get("ayahs", 0),
                    language="ar"
                ))
            
            return QuranData(
                languages=[
                    Language(code="ar", name="Arabic", native_name="العربية", rtl=True),
                    Language(code="en", name="English", native_name="English", rtl=False),
                ],
                reciters=reciters,
                surahs=surahs,
                cached_at=None,
                language="ar",
                version="1.0"
            )
        except Exception as e:
            self.logger.error(f"Failed to load default data: {e}")
            # Return minimal data
            return QuranData(
                languages=[Language(code="ar", name="Arabic", native_name="العربية", rtl=True)],
                reciters=[],
                surahs=[],
                cached_at=None,
                language="ar",
                version="1.0"
            )
    
    def refresh(self) -> QuranData:
        """Force refresh data from API."""
        self._data = None
        return self.load_data(force_refresh=True)
    
    def get_reciters(self) -> List[Reciter]:
        """Get list of reciters."""
        return self.data.reciters
    
    def get_surahs(self) -> List[Surah]:
        """Get list of surahs."""
        return self.data.surahs
    
    def get_languages(self) -> List[Language]:
        """Get list of available languages."""
        return self.data.languages
    
    def get_reciter_by_code(self, code: str) -> Optional[Reciter]:
        """Get reciter by code."""
        return self.data.get_reciter_by_code(code)
    
    def get_reciter_by_id(self, reciter_id: int) -> Optional[Reciter]:
        """Get reciter by ID."""
        return self.data.get_reciter_by_id(reciter_id)
    
    def get_surah_by_id(self, surah_id: int) -> Optional[Surah]:
        """Get surah by ID."""
        return self.data.get_surah_by_id(surah_id)
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            self.logger.info("Cleared all cached data")
            self._data = None
        except Exception as e:
            raise CacheError(f"Failed to clear cache: {e}") from e
