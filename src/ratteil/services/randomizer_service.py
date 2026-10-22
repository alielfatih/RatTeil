import random as r
from ratteil.models.reciter import Reciter
from ratteil.models.surah import SurahInfo

class RandomizerService:
    @staticmethod
    def get_available_reciters_list(reciters_codes_db: list, reciters_db: dict) -> list[str]:
        reciters_list = []
        for code in reciters_codes_db:
            reciter = Reciter(code, reciters_db)
            reciters_list.append(f"code: {reciter.code}\tname: {reciter.name}")
        return reciters_list
        
    @staticmethod
    def get_reciters_with_multi_moshafs(reciters_codes_db: list, reciters_db: dict) -> list[str]:
        multi_reciters = []
        for code in reciters_codes_db:
            reciter = Reciter(code, reciters_db)
            if reciter.have_multi_moshafs:
                multi_reciters.append(code)
        return multi_reciters
    
    @staticmethod
    def generate_random_reciters_list(list_length: int, reciters_codes_list: list, reciters_db: dict) -> tuple[list[str], list[str]]:
        temp_list = []
        if list_length > len(reciters_codes_list):
            if len(reciters_codes_list) == 1:
                list_length = 1
            elif len(reciters_codes_list) < 10:
                list_length = r.randrange(1, len(reciters_codes_list) + 1)
            else:
                list_length = r.randrange(3, 6)
                
        while len(temp_list) != list_length:
            reciter_code = r.choice(reciters_codes_list)
            if reciter_code not in temp_list:
                temp_list.append(reciter_code)
                
        selected_surahs_list = []
        for x in temp_list:
            reciter = Reciter(x, reciters_db)
            for i in reciter.selected_moshaf_surahs_list:
                s = SurahInfo(i, x, reciter.selected_moshaf_type, reciters_db)
                selected_surahs_list.append(f"audios/{s.dl_name}")
                
        return temp_list, selected_surahs_list

    @staticmethod
    def generate_random_surahs_list(list_length: int, surah_index: int | None, selected_surahs_pool: list[str]) -> list[str]:
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