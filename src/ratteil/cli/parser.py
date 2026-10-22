import argparse
import random as r

def create_parser(reciters_codes: list) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="RatTeil",
        description="Stream The Holy Quran to a YouTube channel.",
        epilog="""
    RatTeil  Copyright (C) 2024  Ali Elfatih. \n
    This program comes with ABSOLUTELY NO WARRANTY. \n
    This is free software, and you are welcome to redistribute it under certain conditions; \n \t type `ratteil -c' for details.
    Made with ♡ & ^_^ by Moddaker Team""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-c", "--copyright", help="Show Copyright LICENSE.", action="store_const", const=True, dest="copyright")
    parser.add_argument("-l", "--list", metavar="", help="available reciters", action="store_const", const=True, default=False, dest="reciters_list")
    parser.add_argument("-mx", "--max", metavar="", help="max stream length in minutes", type=float, default=450, dest="max_len")
    parser.add_argument("-m", "--min", metavar="", type=float, help="minimum streams length in minutes", default=120.0, dest="minimum_stream_length")
    parser.add_argument("-ms", "--streams", metavar="", type=float, help="minimum streams number. Note that each stream'll be 75 minute or less", dest="stream_numbers")
    parser.add_argument("-n", metavar="", type=int, help="number of reciters per stream", default=r.randrange(3, 7), dest="reciters_number")
    parser.add_argument("-R", "--reciter", metavar="", help="choose reciter or reciters by code", dest="reciter", nargs="*", choices=reciters_codes)
    parser.add_argument("-r", "--resume", metavar="", help="resume previous stream", action="store_const", const=True, default=False, dest="resume_stream")
    parser.add_argument("-sn", metavar="", type=int, help="Surahs number per stream", default=r.randrange(20, 50), dest="surahs_number")
    parser.add_argument("-s", "--surah", metavar="", type=int, choices=list(range(1, 115)), help="choose surah by index", dest="surah")
    parser.add_argument("--no-download", metavar="", default=False, help="stream existing files; no new downloads", dest="no_download", action='store_const', const=True)
    parser.add_argument("--no-validation", metavar="", help="stop minimum streams validation", default=False, action="store_const", const=True, dest="no_validation")
    parser.add_argument("-t", "--sites", metavar="", help="site to stream to", dest="sites", choices=["youtube", "yt", "fb", "facebook"], nargs="*")
    parser.add_argument("-d", "--dev", dest="dev", action="store_const", const=True)
    return parser