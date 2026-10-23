"""
Reciter model for RatTeil application.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import random as r


@dataclass
class Reciter:
    """
    Information about a Quran reciter.
    
    Attributes:
        reciter_id: The reciter ID (primary identifier)
        code: The reciter code (for backward compatibility, computed from reciter_id)
        reciters_db: The reciters database (excluded from repr)
        name: The reciter name (computed)
        moshafs: List of available moshafs (computed)
        have_multi_moshafs: Whether the reciter has multiple moshafs (computed)
        select_moshaf: The selected moshaf (computed)
        selected_moshaf_type: The selected moshaf type (computed)
        selected_moshaf_surahs_list: List of surahs in the selected moshaf (computed)
        selected_moshaf_url: The URL of the selected moshaf (computed)
    """
    reciter_id: int | str
    code: str = field(init=False)
    reciters_db: Dict = field(repr=False)
    name: str = field(init=False)
    moshafs: List = field(init=False)
    have_multi_moshafs: bool = field(init=False)
    select_moshaf: Dict = field(init=False)
    selected_moshaf_type: int = field(init=False)
    selected_moshaf_surahs_list: List = field(init=False)
    selected_moshaf_url: str = field(init=False)

    def __post_init__(self):
        """Initialize computed fields."""
        from ratteil.reciters import reciters_by_id
        
        # Get code from reciter_id for backward compatibility
        if isinstance(self.reciter_id, int):
            self.code = reciters_by_id.get(self.reciter_id, str(self.reciter_id))
        else:
            self.code = reciters_by_id.get(int(self.reciter_id), str(self.reciter_id))
        
        reciter_data = self.reciters_db.get(self.code, {})
        self.name = reciter_data.get("name", "")
        self.moshafs = reciter_data.get("moshaf", [])
        self.have_multi_moshafs = len(self.moshafs) > 1
        
        if self.moshafs:
            self.select_moshaf = r.choice(self.moshafs)
            self.selected_moshaf_type = self.select_moshaf.get("moshaf_type", 0)
            surah_list_str = self.select_moshaf.get("surah_list", "")
            self.selected_moshaf_surahs_list = surah_list_str.split(",") if surah_list_str else []
            self.selected_moshaf_url = self.select_moshaf.get("server", "")
        else:
            self.select_moshaf = {}
            self.selected_moshaf_type = 0
            self.selected_moshaf_surahs_list = []
            self.selected_moshaf_url = ""

    def get_moshaf_name_url(self, mtype: int, url: bool = False) -> str:
        """
        Get moshaf name or URL by type.
        
        Args:
            mtype: The moshaf type
            url: If True, return URL; otherwise return name
            
        Returns:
            The moshaf name or URL
        """
        for x in self.moshafs:
            if x.get("moshaf_type") == mtype:
                return x.get("server") if url else x.get("name")
        return ""
