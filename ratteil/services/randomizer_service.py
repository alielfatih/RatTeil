"""Randomizer service for generating random selections."""

import random
from typing import List, Optional

from ratteil.config import get_settings
from ratteil.models.surah import Surah
from ratteil.models.reciter import Reciter
from ratteil.repositories.surah_repository import SurahRepository, LocalSurahRepository
from ratteil.repositories.reciter_repository import ReciterRepository, LocalReciterRepository


class RandomizerService:
    """Service for generating random selections of surahs and reciters."""
    
    def __init__(
        self,
        surah_repository: Optional[SurahRepository] = None,
        reciter_repository: Optional[ReciterRepository] = None,
    ):
        """Initialize the randomizer service."""
        self.settings = get_settings()
        self.surah_repository = surah_repository or LocalSurahRepository()
        self.reciter_repository = reciter_repository or LocalReciterRepository()
    
    def generate_random_surahs_list(
        self,
        count: Optional[int] = None,
        exclude: Optional[List[int]] = None,
    ) -> List[Surah]:
        """Generate a list of random surahs.
        
        Args:
            count: Number of surahs to select (default from settings)
            exclude: List of surah IDs to exclude
            
        Returns:
            List of random Surah objects
        """
        count = count or self.settings.MAX_SURAHS
        exclude = exclude or []
        
        all_surahs = self.surah_repository.get_all()
        
        # Filter out excluded surahs
        available_surahs = [
            s for s in all_surahs if s.id not in exclude
        ]
        
        if not available_surahs:
            raise ValueError("No surahs available after exclusions")
        
        return random.sample(
            available_surahs,
            min(count, len(available_surahs)),
        )
    
    def generate_random_reciters_list(
        self,
        count: Optional[int] = None,
        with_multiple_moshafs: bool = False,
        exclude: Optional[List[str]] = None,
    ) -> List[Reciter]:
        """Generate a list of random reciters.
        
        Args:
            count: Number of reciters to select (default from settings)
            with_multiple_moshafs: Only select reciters with multiple moshafs
            exclude: List of reciter IDs to exclude
            
        Returns:
            List of random Reciter objects
        """
        count = count or self.settings.MAX_RECITERS
        exclude = exclude or []
        
        if with_multiple_moshafs:
            all_reciters = self.reciter_repository.get_with_multiple_moshafs()
        else:
            all_reciters = self.reciter_repository.get_all()
        
        # Filter out excluded reciters
        available_reciters = [
            r for r in all_reciters if r.id not in exclude
        ]
        
        if not available_reciters:
            raise ValueError("No reciters available after exclusions")
        
        return random.sample(
            available_reciters,
            min(count, len(available_reciters)),
        )
    
    def generate_random_combination(
        self,
        surahs_count: Optional[int] = None,
        reciters_count: Optional[int] = None,
        reciters_with_multiple_moshafs: bool = False,
    ) -> tuple:
        """Generate a random combination of surahs and reciters.
        
        Args:
            surahs_count: Number of surahs to select
            reciters_count: Number of reciters to select
            reciters_with_multiple_moshafs: Only select reciters with multiple moshafs
            
        Returns:
            Tuple of (List[Surah], List[Reciter])
        """
        surahs = self.generate_random_surahs_list(surahs_count)
        reciters = self.generate_random_reciters_list(
            reciters_count,
            with_multiple_moshafs=reciters_with_multiple_moshafs,
        )
        
        return surahs, reciters
    
    def get_available_reciters_list(self) -> List[Reciter]:
        """Get list of all available reciters.
        
        Returns:
            List of all Reciter objects
        """
        return self.reciter_repository.get_all()
    
    def get_reciters_with_multi_moshafs(self) -> List[Reciter]:
        """Get list of reciters with multiple moshafs.
        
        Returns:
            List of Reciter objects with multiple moshafs
        """
        return self.reciter_repository.get_with_multiple_moshafs()
