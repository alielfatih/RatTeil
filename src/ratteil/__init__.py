"""
RatTeil is an app to live stream the Holy Quran to YouTube.
Copyright (C) 2024  Ali Elfatih
"""

from ratteil.config.settings import get_settings
from ratteil.config.constants import DEFAULT_DATA_DIR, DEFAULT_FIXER_DIR, DEFAULT_IMG_DIR
from pathlib import Path
from ratteil.cli.parser import create_parser
from ratteil.cli.commands import pre_launcher, handle_reciters_list, handle_copyright
from ratteil.reciters import reciters_code as recitersCodesDB, reciters as recitersDB
import sys
import os

RATTEIL_PATH = Path(__file__).resolve().parent
RATTEIL_RESOURCES = get_settings().data_dir

def ensure_resources_initialized(resources_path: Path, package_path: Path) -> None:
    """Initializes necessary folders and resources on first run."""
    if not resources_path.exists():
        resources_path.mkdir(parents=True, exist_ok=True)
        (resources_path / "audios").mkdir(exist_ok=True)
        (resources_path / "imgs").mkdir(exist_ok=True)
        (resources_path / "fixer").mkdir(exist_ok=True)
        (resources_path / "fb_stream").mkdir(exist_ok=True)
        
        fixer_src = package_path / "fixer"
        imgs_src = package_path / "imgs"
        
        if fixer_src.exists():
            import shutil
            shutil.copytree(fixer_src, resources_path / "fixer", dirs_exist_ok=True)
        if imgs_src.exists(): 
            import shutil
            shutil.copytree(imgs_src, resources_path / "imgs", dirs_exist_ok=True)

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