"""
Surah model for RatTeil application.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

from ratteil.utils.file_utils import surah_index_to_filename


@dataclass
class SurahInfo:
    """
    Information about a Quran surah.
    
    Attributes:
        index: The surah index (1-114)
        code: The reciter code
        mtype: The moshaf type
        reciters_db: The reciters database (excluded from repr)
        id: The surah ID (computed from index)
        name: The surah name
        reciter: The reciter object
        moshaf: The moshaf name
        dl_name: The download filename
        url: The base URL for the surah audio
    """
    index: int | str
    code: str
    mtype: int | str
    reciters_db: Dict = field(repr=False)
    
    id: str = field(init=False)
    name: str = field(init=False)
    reciter: Any = field(init=False)  # Will be Reciter type after circular import resolution
    moshaf: str = field(init=False)
    dl_name: str = field(init=False)
    url: str = field(init=False)

    def __post_init__(self):
        """Initialize computed fields."""
        # Import here to avoid circular imports
        from ratteil.models.reciter import Reciter
        from ratteil.surahs import surah_list as su_list
        
        self.id = str(self.index)
        surah_key = f"surah_{self.id}"
        self.name = su_list.get(surah_key, {}).get("name", "")
        self.reciter = Reciter(self.code, self.reciters_db)
        self.moshaf = self.reciter.get_moshaf_name_url(int(self.mtype))
        self.dl_name = f"{self.code}@@{self.mtype}@@{self.id}.mp3"
        self.url = self.reciter.get_moshaf_name_url(int(self.mtype), True)

    def __str__(self) -> str:
        """String representation of the surah."""
        if "\u0627\u0644\u0645\u0635\u062d\u0641" in self.moshaf or "\u0642\u0631\u0627\u0626\u0647" in self.moshaf:
            content = self.moshaf
        else:
            content = f"\u0628\u0631\u0648\u0627\u064a\u0629 {self.moshaf}"
        return f" \u0633\u0648\u0631\u0629 {self.name} {content} \u0628\u0635\u0648\u062a \u0627\u0644\u0642\u0627\u0631\u0646 {self.reciter.name}. " 
    
    def get_audio_url(self) -> str:
        """Get the full audio URL for this surah."""
        return f"{self.url}{surah_index_to_filename(self.id)}"
    
    def get_filepath(self, base_dir: Path) -> Path:
        """Get the local filepath for this surah."""
        return base_dir / self.dl_name
