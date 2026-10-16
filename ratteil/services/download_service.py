"""Download service for downloading audio files."""

import os
import requests
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import urlparse

from ratteil.config import get_settings, DownloadError
from ratteil.models.surah import Surah
from ratteil.models.reciter import Reciter, Moshaf


class DownloadService:
    """Service for downloading audio files from various sources."""
    
    def __init__(self):
        """Initialize the download service."""
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"RatTeil/{self.settings.APP_VERSION}",
        })
    
    def download(
        self,
        url: str,
        output_path: Union[str, Path],
        chunk_size: int = 8192,
    ) -> Path:
        """Download a file from a URL.
        
        Args:
            url: URL to download from
            output_path: Path to save the file
            chunk_size: Chunk size for streaming download
            
        Returns:
            Path to the downloaded file
            
        Raises:
            DownloadError: If download fails
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            return output_path
        except requests.RequestException as e:
            raise DownloadError(f"Failed to download {url}: {e}") from e
    
    def download_surah_audio(
        self,
        surah: Surah,
        reciter: Reciter,
        moshaf: Optional[Moshaf] = None,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Download audio for a specific surah by a reciter.
        
        Args:
            surah: The surah to download
            reciter: The reciter
            moshaf: Optional specific moshaf to use
            output_dir: Optional output directory
            
        Returns:
            Path to the downloaded file
        """
        # Use first moshaf if none specified
        if moshaf is None and reciter.moshafs:
            moshaf = reciter.moshafs[0]
        
        if moshaf is None:
            raise DownloadError(
                f"No moshaf available for reciter {reciter.id}"
            )
        
        # Generate filename
        output_dir = output_dir or (self.settings.AUDIO_DIR / reciter.id)
        filename = f"{surah.id:03d}_{surah.name.replace(' ', '_')}_{reciter.id}.mp3"
        output_path = output_dir / filename
        
        # Build URL
        url = self._build_audio_url(surah, reciter, moshaf)
        
        return self.download(url, output_path)
    
    def _build_audio_url(
        self,
        surah: Surah,
        reciter: Reciter,
        moshaf: Moshaf,
    ) -> str:
        """Build the audio URL for a surah.
        
        This should be customized based on the actual API being used.
        """
        # This is a placeholder - actual implementation depends on the API
        # For example, using Quran.com API or custom endpoint
        return moshaf.url.format(
            surah_id=surah.id,
            reciter_id=reciter.id,
        )
    
    def download_batch(
        self,
        surahs: List[Surah],
        reciter: Reciter,
        output_dir: Optional[Path] = None,
    ) -> List[Path]:
        """Download audio for multiple surahs by a reciter.
        
        Args:
            surahs: List of surahs to download
            reciter: The reciter
            output_dir: Optional output directory
            
        Returns:
            List of paths to downloaded files
        """
        downloaded_files = []
        output_dir = output_dir or (self.settings.AUDIO_DIR / reciter.id)
        
        for surah in surahs:
            try:
                file_path = self.download_surah_audio(
                    surah, reciter, output_dir=output_dir
                )
                downloaded_files.append(file_path)
            except DownloadError as e:
                # Log and continue with next surah
                print(f"Warning: Failed to download {surah.name}: {e}")
                continue
        
        return downloaded_files
    
    def get_existing_files(
        self,
        reciter_id: str,
        audio_dir: Optional[Path] = None,
    ) -> List[Path]:
        """Get list of already downloaded audio files for a reciter.
        
        Args:
            reciter_id: The reciter ID
            audio_dir: Optional audio directory
            
        Returns:
            List of existing audio file paths
        """
        audio_dir = audio_dir or (self.settings.AUDIO_DIR / reciter_id)
        
        if not audio_dir.exists():
            return []
        
        return list(audio_dir.glob("*.mp3"))
