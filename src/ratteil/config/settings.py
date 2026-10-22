from pathlib import Path
import os
import shutil

USER_HOME = Path.home()
RATTEIL_RESOURCES = USER_HOME / "RatTeil-resources"
RATTEIL_PATH = Path(__file__).resolve().parents[1]

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
            shutil.copytree(fixer_src, resources_path / "fixer", dirs_exist_ok=True)
        if imgs_src.exists(): 
            shutil.copytree(imgs_src, resources_path / "imgs", dirs_exist_ok=True)