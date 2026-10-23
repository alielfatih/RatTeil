"""
Randomizer service for RatTeil application.

Provides random selection of reciters and surahs for streaming.
"""

import random as r
from typing import List, Tuple, Optional
from pathlib import Path

from ratteil.models.surah import SurahInfo
from ratteil.models.reciter import Reciter
from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import ValidationError
from ratteil.utils.file_utils import filename_resolve
from ratteil.utils.logging import get_logger


class RandomizerService:
    """
    Service for random selection of reciters and surahs.
    
    Provides methods to generate random lists of reciters and surahs
    for streaming purposes.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize RandomizerService.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or get_settings()
        self.logger = get_logger("ratteil.services.randomizer")

    @staticmethod
    def get_available_reciters_list(reciters_ids_db: List[int | str], reciters_db: dict) -> List[str]:
        """
        Get formatted list of available reciters.
        
        Args:
            reciters_ids_db: List of reciter IDs
            reciters_db: Reciters database
            
        Returns:
            List of formatted strings describing each reciter
        """
        from ratteil.reciters import reciters_by_id
        reciters_list = []
        for reciter_id in reciters_ids_db:
            code = reciters_by_id.get(reciter_id, str(reciter_id))
            reciter = Reciter(reciter_id, reciters_db)
            reciters_list.append(f"code: {reciter.code}\tname: {reciter.name}")
        return reciters_list
        
    @staticmethod
    def get_reciters_with_multi_moshafs(reciters_ids_db: List[int | str], reciters_db: dict) -> List[int | str]:
        """
        Get list of reciters with multiple moshafs.
        
        Args:
            reciters_ids_db: List of reciter IDs
            reciters_db: Reciters database
            
        Returns:
            List of reciter IDs that have multiple moshafs
        """
        from ratteil.reciters import reciters_by_id
        multi_reciters = []
        for reciter_id in reciters_ids_db:
            code = reciters_by_id.get(reciter_id, str(reciter_id))
            reciter = Reciter(reciter_id, reciters_db)
            if reciter.have_multi_moshafs:
                multi_reciters.append(reciter_id)
        return multi_reciters
    
    @staticmethod
    def generate_random_reciters_list(
        list_length: int,
        reciters_ids_list: List[int | str],
        reciters_db: dict
    ) -> Tuple[List[int | str], List[str]]:
        """
        Generate random list of reciters and their surahs.
        
        Args:
            list_length: Number of reciters to select
            reciters_ids_list: List of available reciter IDs
            reciters_db: Reciters database
            
        Returns:
            Tuple of (selected_reciter_ids, selected_surahs_list)
        """
        from ratteil.reciters import reciters_by_id
        temp_list = []
        if list_length > len(reciters_ids_list):
            if len(reciters_ids_list) == 1:
                list_length = 1
            elif len(reciters_ids_list) < 10:
                list_length = r.randrange(1, len(reciters_ids_list) + 1)
            else:
                list_length = r.randrange(3, 6)
                
        while len(temp_list) != list_length:
            reciter_id = r.choice(reciters_ids_list)
            if reciter_id not in temp_list:
                temp_list.append(reciter_id)
                
        selected_surahs_list = []
        for x in temp_list:
            reciter = Reciter(x, reciters_db)
            for i in reciter.selected_moshaf_surahs_list:
                s = SurahInfo(i, x, reciter.selected_moshaf_type, reciters_db)
                selected_surahs_list.append(f"audios/{s.dl_name}")
                
        return temp_list, selected_surahs_list

    @staticmethod
    def generate_random_surahs_list(
        list_length: int,
        surah_index: Optional[int],
        selected_surahs_pool: List[str]
    ) -> List[str]:
        """
        Generate random list of surahs from the pool.
        
        Args:
            list_length: Number of surahs to select
            surah_index: Optional specific surah index to use
            selected_surahs_pool: List of available surahs
            
        Returns:
            List of selected surah file paths
        """
        temp_list = []
        pool_copy = list(selected_surahs_pool)
        
        if list_length > len(pool_copy):
            list_length = len(pool_copy)
            
        while len(temp_list) != list_length and pool_copy:
            if not surah_index:
                x = r.choice(pool_copy)
            else:
                shrank_list = [i for i in pool_copy if f"@@{surah_index}.mp3" in i]
                if not shrank_list:
                    break
                x = r.choice(shrank_list)
            pool_copy.remove(x)
            temp_list.append(x)
        return temp_list
