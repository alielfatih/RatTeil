"""
Download service for RatTeil application.

Provides functionality to download Quran audio files.
"""

import os
import glob as g
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from ratteil.models.surah import SurahInfo
from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import DownloadError, ValidationError
from ratteil.repositories.surah_repository import SurahRepository
from ratteil.services.audio_service import AudioService
from ratteil.utils.file_utils import filename_resolve, surah_index_to_filename
from ratteil.utils.logging import get_logger


class DownloadService:
    """
    Service for downloading Quran audio files.
    
    Uses the SurahRepository and AudioService to download and manage audio files.
    """
    
    def __init__(
        self,
        surah_repository: Optional[SurahRepository] = None,
        audio_service: Optional[AudioService] = None,
        settings: Optional[Settings] = None
    ):
        """
        Initialize DownloadService.
        
        Args:
            surah_repository: Surah repository instance
            audio_service: Audio service instance
            settings: Application settings
        """
        self.settings = settings or get_settings()
        self.surah_repository = surah_repository or SurahRepository()
        self.audio_service = audio_service or AudioService(settings)
        self.logger = get_logger("ratteil.services.download")
    
    async def download_audios(
        self,
        max_len: float,
        surahs_list: List[str],
        reciters_db: Dict,
        resources_path: Path,
        validation: bool = False,
        previous_len: Optional[float] = None
    ) -> Tuple[float, bool]:
        """
        Download audio files for the stream.
        
        Args:
            max_len: Maximum total length in minutes
            surahs_list: List of surah file paths (e.g., "audios/alafasy@@1@@1.mp3")
            reciters_db: Reciters database
            resources_path: Base resources directory
            validation: Whether this is for validation only
            previous_len: Previous total length
            
        Returns:
            Tuple of (current_length, max_reached)
        """
        max_st = False
        current_len = previous_len or 0.0
        ensure_max = []
        
        download_path = Path(resources_path) / "audios"
        download_path.mkdir(parents=True, exist_ok=True)
        
        if not validation:
            # Clean up old files not in surahs_list
            old_files = g.glob(str(download_path / "*"))
            if len(old_files) >= 1:
                for file in old_files:
                    y = file.split("/")[-1]
                    z = f"audios/{y}"
                    if z not in surahs_list:
                        os.remove(file)
                    else:
                        surahs_list.remove(z)
                        file_len = self.audio_service.get_audio_length(file)
                        current_len += file_len
                        ensure_max.append({
                            "file": file,
                            "file_len": file_len,
                            "less10": file_len < 10
                        })
        
        for x in surahs_list:
            # filename_resolve returns (index, code, mtype) but SurahInfo now uses reciter_id
            # We need to get reciter_id from code
            from ratteil.reciters import reciters_by_id
            parts = filename_resolve(x)
            if len(parts) >= 3:
                index, code, mtype = parts[0], parts[1], parts[2]
                reciter_id = None
                for rid, c in reciters_by_id.items():
                    if c == code:
                        reciter_id = rid
                        break
                if reciter_id is None:
                    reciter_id = code
                surah = SurahInfo(index, reciter_id, mtype, reciters_db)
            else:
                surah = SurahInfo(*parts, reciters_db)
            surah_path = download_path / surah.dl_name
            url = f"{surah.url}{surah_index_to_filename(surah.id)}"
            
            if not surah_path.exists():
                if current_len < max_len:
                    # Download synchronously for now (will be async in future)
                    import subprocess
                    try:
                        subprocess.run(
                            ["wget", url, "-O", str(surah_path)],
                            check=True,
                            capture_output=True
                        )
                        file_len = self.audio_service.get_audio_length(surah_path)
                        current_len += file_len
                        ensure_max.append({
                            "file": surah_path,
                            "file_len": file_len,
                            "less10": file_len < 10
                        })
                    except subprocess.CalledProcessError as e:
                        self.logger.error(f"Failed to download {url}: {e}")
                        if surah_path.exists():
                            surah_path.unlink()
                else:
                    max_st = True
        
        # Clean up to stay within max_len
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
        
        self.logger.debug(f"Current length: {current_len}")
        return current_len, max_st
