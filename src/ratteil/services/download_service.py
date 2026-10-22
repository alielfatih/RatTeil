import os
import glob as g
from pathlib import Path
from ratteil.models.surah import SurahInfo
from ratteil.utils.file_utils import filename_resolve, surah_index_to_filename
from ratteil.services.audio_service import get_audio_length

def download_audios(streamer, max_len: float, surahs_list: list[str], reciters_db: dict, resources_path: Path, validation: bool = False, previous_len: float | None = None) -> tuple[float, bool]:
    """Download audio files for the stream."""
    max_st = False
    current_len = 0.0
    ensure_max = []
    
    if previous_len:
        current_len = previous_len
    
    download_path = Path(resources_path) / "audios"
    download_path.mkdir(parents=True, exist_ok=True)
    
    if not validation:  # avoid deleting audios on validation process
        old_files = g.glob(str(download_path / "*"))
        if len(old_files) >= 1:
            for file in old_files:
                y = file.split("/")[-1]
                z = f"audios/{y}"
                if z not in surahs_list:
                    os.remove(file)
                else:
                    surahs_list.remove(z)
                    file_len = get_audio_length(file)
                    current_len += file_len
                    ensure_max.append({
                        "file": file,
                        "file_len": file_len,
                        "less10": file_len < 10
                    })

    for x in surahs_list:
        surah = SurahInfo(*filename_resolve(x), reciters_db)
        surah_path = download_path / surah.dl_name
        url = f"{surah.url}{surah_index_to_filename(surah.id)}"
        
        if not surah_path.exists():
            if current_len < max_len:
                os.system(f"wget {url} -O {surah_path}")
                file_len = get_audio_length(surah_path)
                current_len += file_len
                ensure_max.append({
                    "file": surah_path,
                    "file_len": file_len,
                    "less10": file_len < 10
                })
            else:
                max_st = True

    # current length to max_length reminder cleanup
    cur_mx_rem = abs(current_len - max_len)
    if cur_mx_rem > 1:
        for _ in range(1, 3):
            for i in list(ensure_max):
                xyz = abs(current_len - i["file_len"])
                if xyz >= (max_len + 3) or (xyz >= max_len + 1 and xyz <= (max_len + 1)):
                    current_len -= i["file_len"]
                    if os.path.exists(i["file"]):
                        os.remove(i["file"])
                    ensure_max.remove(i)
        print("current : ", current_len)
        
    return current_len, max_st