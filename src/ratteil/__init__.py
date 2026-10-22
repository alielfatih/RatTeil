"""
RatTeil is an app to live stream the Holy Quran to YouTube.
Copyright (C) 2024  Ali Elfatih
"""

from ratteil.config.settings import RATTEIL_RESOURCES, RATTEIL_PATH, ensure_resources_initialized
from ratteil.cli.parser import create_parser
from ratteil.cli.commands import pre_launcher, handle_reciters_list, handle_copyright
from ratteil.reciters import reciters_code as recitersCodesDB, reciters as recitersDB
import sys
import os

def ratteil():
    ensure_resources_initialized(RATTEIL_RESOURCES, RATTEIL_PATH)
    
    parser = create_parser(recitersCodesDB)
    args = parser.parse_args()
    
    active_reciters_db = recitersDB
    if args.dev:
        from ratteil.base_test import recs as active_reciters_db
        
    if ((not args.sites) and (not args.reciters_list)) and (not args.copyright):
        os.system("clear" if os.name == 'posix' else 'cls')
        print("!! sites are required at least one site !! \n")
        print("ex:\n $ ratteil -t youtube \n")
        sys.exit(0)
        
    if args.reciters_list:
        handle_reciters_list(active_reciters_db, recitersCodesDB, RATTEIL_RESOURCES, RATTEIL_PATH)
    elif args.copyright:
        handle_copyright(RATTEIL_PATH)
    else:
        pre_launcher(args, active_reciters_db, recitersCodesDB, RATTEIL_RESOURCES, RATTEIL_PATH)