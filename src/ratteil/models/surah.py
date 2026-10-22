from dataclasses import dataclass, field
from ratteil.models.reciter import Reciter
from ratteil.surahs import surah_list as su_list

@dataclass
class SurahInfo:
    index: int | str
    code: str
    mtype: int | str
    reciters_db: dict = field(repr=False)
    
    id: str = field(init=False)
    name: str = field(init=False)
    reciter: Reciter = field(init=False)
    moshaf: str = field(init=False)
    dl_name: str = field(init=False)
    url: str = field(init=False)

    def __post_init__(self):
        self.id = str(self.index)
        surah_key = f"surah_{self.id}"
        self.name = su_list.get(surah_key, {}).get("name", "")
        self.reciter = Reciter(self.code, self.reciters_db)
        self.moshaf = self.reciter.get_moshaf_name_url(int(self.mtype))
        self.dl_name = f"{self.code}@@{self.mtype}@@{self.id}.mp3"
        self.url = self.reciter.get_moshaf_name_url(int(self.mtype), True)

    def __str__(self) -> str:
        if "المصحف" in self.moshaf or "قراءة" in self.moshaf:
            content = self.moshaf
        else:
            content = f"برواية {self.moshaf}"
        return f" سورة {self.name} {content} بصوت القاريء {self.reciter.name}." 