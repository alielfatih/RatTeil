from dataclasses import dataclass, field
import random as r

@dataclass
class Reciter:
    code: str
    reciters_db: dict = field(repr=False)
    name: str = field(init=False)
    moshafs: list = field(init=False)
    have_multi_moshafs: bool = field(init=False)
    select_moshaf: dict = field(init=False)
    selected_moshaf_type: int = field(init=False)
    selected_moshaf_surahs_list: list = field(init=False)
    selected_moshaf_url: str = field(init=False)

    def __post_init__(self):
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
        for x in self.moshafs:
            if x.get("moshaf_type") == mtype:
                return x.get("server") if url else x.get("name")
        return "" 