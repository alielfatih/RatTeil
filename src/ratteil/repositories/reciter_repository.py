"""
Reciter repository implementation.

This repository provides access to Reciter data and operations.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from ratteil.models.reciter import Reciter
from ratteil.repositories.protocols import ReciterRepositoryProtocol
from ratteil.config.settings import get_settings


class ReciterRepository(ReciterRepositoryProtocol):
    """
    Local implementation of ReciterRepositoryProtocol.
    
    This repository uses the local reciters.py data file to provide
    information about Quran reciters.
    """
    
    def __init__(self, reciters_db: Optional[Dict] = None):
        """
        Initialize ReciterRepository.
        
        Args:
            reciters_db: Dictionary containing reciter data.
                        If None, will be loaded from ratteil.reciters.
        """
        self.reciters_db = reciters_db or {}
        if not self.reciters_db:
            from ratteil.reciters import reciters
            self.reciters_db = reciters
    
    def get_reciter(self, reciter_id: int | str) -> Reciter:
        """
        Get a single reciter by ID.
        
        Args:
            reciter_id: The reciter ID
            
        Returns:
            Reciter: The reciter information
        """
        return Reciter(reciter_id, self.reciters_db)
    
    def get_reciters(self, reciter_ids: List[int | str]) -> List[Reciter]:
        """
        Get multiple reciters by IDs.
        
        Args:
            reciter_ids: List of reciter IDs
            
        Returns:
            List[Reciter]: List of reciter information
        """
        return [self.get_reciter(reciter_id) for reciter_id in reciter_ids]
    
    def list_all_reciters(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available reciters.
        
        Returns:
            Dictionary containing all reciter data
        """
        return self.reciters_db
    
    def get_reciters_with_multi_moshafs(self) -> List[int | str]:
        """
        Get list of reciters with multiple moshafs.
        
        Returns:
            List of reciter IDs that have multiple moshafs
        """
        from ratteil.reciters import reciters_by_id
        multi_reciters = []
        for code, reciter_data in self.reciters_db.items():
            moshafs = reciter_data.get("moshaf", [])
            if len(moshafs) > 1:
                reciter_id = reciter_data.get("id")
                if reciter_id:
                    multi_reciters.append(reciter_id)
        return multi_reciters
    
    def search_reciters(self, query: str, limit: int = 10) -> List[Reciter]:
        """
        Search reciters by name.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching Reciter objects
        """
        results = []
        query_lower = query.lower()
        
        for code, reciter_data in self.reciters_db.items():
            if query_lower in reciter_data.get("name", "").lower():
                results.append(Reciter(code, self.reciters_db))
                if len(results) >= limit:
                    break
        
        return results
    
    def get_available_reciters_list(self) -> List[str]:
        """
        Get formatted list of available reciters.
        
        Returns:
            List of formatted strings describing each reciter
        """
        reciters_list = []
        for code in self.reciters_db.keys():
            reciter = Reciter(code, self.reciters_db)
            reciters_list.append(f"code: {reciter.code}\tname: {reciter.name}")
        return reciters_list
