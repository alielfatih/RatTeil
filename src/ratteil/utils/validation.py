import glob as g
from ratteil.models.surah import SurahInfo
from ratteil.utils.file_utils import filename_resolve
from ratteil.services.audio_service import AudioService
from ratteil.services.randomizer_service import RandomizerService
from ratteil.services.download_service import DownloadService

def stream_validation(streamer, max_len: float, stream_files: list[str], minimum: float, reciters_code: list[str], previous_len: float, surah_index: int | None, reciters_db: dict, resources_path) -> float:
    """Assure audio files duration up to the minimum."""
    duration = 0.0
    if previous_len:
        duration = previous_len
    else:
        for file in stream_files:
            file_len = AudioService().get_audio_length(file)
            if file_len > 0.0:
                duration += file_len
            else:
                stream_files.remove(file)
    
    if minimum > max_len:
        minimum = max_len 
        
    while duration < minimum:
        if len(g.glob(f"{resources_path}/audios/*")) != len(streamer.reciters_list if hasattr(streamer, 'reciters_list') else reciters_code):
            _, selected_pool = RandomizerService.generate_random_reciters_list(1, reciters_code, reciters_db)
            surah_list = RandomizerService.generate_random_surahs_list(1, surah_index, selected_pool)
            if not surah_list:
                break
            x = surah_list[0]
            surah = SurahInfo(*filename_resolve(x), reciters_db).dl_name
            new_len, max_st = download_service.download_audios(streamer, max_len, [x], reciters_db, resources_path, True, duration)
            duration = new_len
            if max_st:
                break
        else:
            minimum = duration
            break
            
    return duration