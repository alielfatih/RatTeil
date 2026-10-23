"""
Surah repository implementation.

This repository provides access to Surah data and operations.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from ratteil.models.surah import SurahInfo
from ratteil.repositories.protocols import SurahRepositoryProtocol
from ratteil.config.settings import get_settings
from ratteil.utils.file_utils import surah_index_to_filename


class SurahRepository(SurahRepositoryProtocol):
    """
    Local implementation of SurahRepositoryProtocol.
    
    This repository uses the local surahs.py data file to provide
    information about Quran surahs.
    """
    
    def __init__(self, surahs_db: Optional[Dict] = None):
        """
        Initialize SurahRepository.
        
        Args:
            surahs_db: Dictionary containing surah data.
                      If None, will be loaded from ratteil.surahs.
        """
        self.surahs_db = surahs_db or {}
        if not self.surahs_db:
            from ratteil.surahs import surah_list
            self.surahs_db = surah_list
    
    def get_surah(self, surah_id: int | str, reciter_id: int | str, moshaf_type: int | str) -> SurahInfo:
        """
        Get a single surah by ID, reciter ID, and moshaf type.
        
        Args:
            surah_id: The surah ID (1-114)
            reciter_id: The reciter ID
            moshaf_type: The moshaf type
            
        Returns:
            SurahInfo: The surah information
        """
        return SurahInfo(
            index=surah_id,
            reciter_id=reciter_id,
            mtype=moshaf_type,
            reciters_db={}
        )
    
    def get_surahs(self, surah_ids: List[int | str], reciter_id: int | str, moshaf_type: int | str) -> List[SurahInfo]:
        """
        Get multiple surahs by IDs, reciter ID, and moshaf type.
        
        Args:
            surah_ids: List of surah IDs
            reciter_id: The reciter ID
            moshaf_type: The moshaf type
            
        Returns:
            List[SurahInfo]: List of surah information
        """
        return [
            self.get_surah(surah_id, reciter_id, moshaf_type)
            for surah_id in surah_ids
        ]
    
    def list_all_surahs(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available surahs.
        
        Returns:
            Dictionary containing all surah data
        """
        return self.surahs_db
    
    def search_surahs(self, query: str, limit: int = 10) -> List[SurahInfo]:
        """
        Search surahs by name or other criteria.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching SurahInfo objects
        """
        results = []
        query_lower = query.lower()
        
        for surah_key, surah_data in self.surahs_db.items():
            if query_lower in surah_data.get("name", "").lower():
                # Extract surah index from key (e.g., "surah_1" -> 1)
                surah_id = surah_key.split("_")[-1]
                results.append(SurahInfo(
                    index=surah_id,
                    reciter_id=0,
                    mtype=1,
                    reciters_db={}
                ))
                if len(results) >= limit:
                    break
        
        return results
    
    def get_surah_audio_url(self, surah: SurahInfo) -> str:
        """
        Get the audio URL for a surah.
        
        Args:
            surah: The SurahInfo object
            
        Returns:
            URL string for the audio file
        """
        return f"{surah.url}{surah_index_to_filename(surah.id)}"
