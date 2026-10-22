import glob as g
import time
import sys
from pathlib import Path
from ratteil.services.stream_service import StreamService
from ratteil.services.randomizer_service import RandomizerService
from ratteil.services.download_service import download_audios
from ratteil.utils.validation import stream_validation

def pre_launcher(options, reciters_db, reciters_codes_db, resources_path, package_path) -> None:
    stream_service = StreamService(reciters_db, resources_path, package_path)
    temp_reciters_list = []
    surah_index = options.surah
    
    if options.reciter:
        temp_reciters_list = options.reciter 
    else:
        temp_reciters_list = reciters_codes_db
    
    selected_surahs_list = []
    if not options.no_download:
        _, selected_surahs_list = RandomizerService.generate_random_reciters_list(
            options.reciters_number, temp_reciters_list, reciters_db
        )
        stream_surahs_list = RandomizerService.generate_random_surahs_list(
            options.surahs_number, surah_index, selected_surahs_list
        )
        
        previous_len, max_st = download_audios(
            stream_service, options.max_len, stream_surahs_list, reciters_db, resources_path
        )
        
        if not options.no_validation:
            minimum_stream_length = 0 
            if options.stream_numbers:
                minimum_stream_length = options.stream_numbers * 75.0
            elif options.surahs_number:
                minimum_stream_length = 0
            else:
                minimum_stream_length = options.minimum_stream_length 
            if not max_st:
                stream_validation(
                    stream_service, options.max_len, g.glob(f"{resources_path}/audios/*"),
                    minimum_stream_length, temp_reciters_list, previous_len, surah_index, reciters_db, resources_path
                )
    
    launcher(stream_service, sites=options.sites)

def launcher(stream_service: StreamService, sites) -> None:
    stream_service.prepare_stream_files(g.glob(f"{stream_service.resources_path}/audios/*"))
    
    for stream in stream_service.streams:
        stream_service.generate_stream_details(stream)
        stream_service.stream(stream, sites)
        time.sleep(60)

def handle_reciters_list(reciters_db, reciters_codes_db, resources_path, package_path) -> None:
    reciters_list = RandomizerService.get_available_reciters_list(reciters_codes_db, reciters_db)
    reciters_list.sort()
    for reciter in reciters_list:
        print(reciter)

def handle_copyright(ratteil_path: Path) -> None:
    copyright_file_path = ratteil_path / "LICENSE"
    if copyright_file_path.exists():
        with open(copyright_file_path, "r", encoding="utf-8") as f:
            for line in f:
                print(line, end="")
    sys.exit(0)