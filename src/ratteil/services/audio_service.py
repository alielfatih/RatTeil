"""
Audio service for RatTeil application.

Provides audio processing functionality including:
- Getting audio file duration
- Merging audio files
- Downloading audio files
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiohttp

from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import AudioProcessingError, DownloadError, FileError
from ratteil.utils.logging import get_logger


class AudioService:
    """
    Service for audio processing operations.
    
    Provides both synchronous and asynchronous methods for audio operations.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize AudioService.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or get_settings()
        self.logger = get_logger("ratteil.services.audio")
    
    def get_audio_length(self, file_path: str | Path) -> float:
        """
        Get audio file duration using ffprobe (synchronous).
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            float: Audio duration in minutes
        """
        try:
            cmd = [
                str(self.settings.ffprobe_path),
                "-i", str(file_path),
                "-show_entries", "format=duration",
                "-v", "quiet",
                "-of", "csv=p=0"
            ]
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode()
            file_length = float(output.strip()) / 60.0
            return float(str(file_length)[:6])
        except (subprocess.CalledProcessError, ValueError) as e:
            self.logger.error(f"Failed to get audio length for {file_path}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return 0.0
    
    async def get_audio_length_async(self, file_path: str | Path) -> float:
        """
        Get audio file duration using ffprobe (asynchronous).
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            float: Audio duration in minutes
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.get_audio_length,
            file_path
        )
    
    def merge_audios(self, audios: List[str | Path], out_path: str | Path) -> Path:
        """
        Merge multiple audio files using ffmpeg (synchronous).
        
        Args:
            audios: List of audio file paths
            out_path: Output file path
            
        Returns:
            Path: Path to the merged audio file
        """
        if not audios:
            raise AudioProcessingError("No audio files to merge", operation="merge")
        
        out_path = Path(out_path)
        merged_output_path = out_path / "fb_stream" / "merged.mp3"
        merged_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing file
        if merged_output_path.exists():
            merged_output_path.unlink()
        
        # Build ffmpeg command
        command = [
            str(self.settings.ffmpeg_path),
            "-loglevel", "error",
        ]
        
        # Add input files
        audio_inputs = []
        for audio in audios:
            command.extend(["-i", str(audio)])
        
        # Add filter complex for concatenation
        filter_inputs = "".join([f"[{i}:a]" for i in range(len(audios))])
        command.extend([
            "-filter_complex",
            f"{filter_inputs}concat=n={len(audios)}:v=0:a=1",
        ])
        
        # Add output
        command.append(str(merged_output_path))
        
        # Execute command
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise AudioProcessingError(
                f"FFmpeg merge failed: {e.stderr.decode()}",
                path=str(merged_output_path),
                operation="merge"
            )
        
        return merged_output_path
    
    async def merge_audios_async(self, audios: List[str | Path], out_path: str | Path) -> Path:
        """
        Merge multiple audio files using ffmpeg (asynchronous).
        
        Args:
            audios: List of audio file paths
            out_path: Output file path
            
        Returns:
            Path: Path to the merged audio file
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.merge_audios,
            audios,
            out_path
        )
    
    async def download_audio(self, url: str, output_path: Path, retry: int = 3) -> float:
        """
        Download audio file with retries.
        
        Args:
            url: URL to download from
            output_path: Path to save the file
            retry: Number of retry attempts
            
        Returns:
            float: Duration of the downloaded audio in minutes
            
        Raises:
            DownloadError: If download fails after all retries
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(retry):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=self.settings.download_timeout) as response:
                        response.raise_for_status()
                        content = await response.read()
                        output_path.write_bytes(content)
                        
                        # Get audio length
                        duration = await self.get_audio_length_async(output_path)
                        return duration
            except Exception as e:
                self.logger.warning(
                    f"Download attempt {attempt + 1} failed for {url}: {e}"
                )
                if attempt < retry - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise DownloadError(
                        f"Failed to download {url} after {retry} attempts",
                        url=url,
                        path=str(output_path)
                    )
        
        return 0.0
    
    async def download_audios(
        self,
        surah_urls: List[str],
        output_dir: Path
    ) -> Dict[str, float]:
        """
        Download multiple audio files concurrently.
        
        Args:
            surah_urls: List of (surah_info, url) tuples
            output_dir: Directory to save files
            
        Returns:
            Dictionary mapping filenames to durations
        """
        semaphore = asyncio.Semaphore(self.settings.max_concurrent_downloads)
        
        async def download_single(url: str, filename: str) -> tuple[str, float]:
            async with semaphore:
                output_path = output_dir / filename
                if output_path.exists():
                    duration = await self.get_audio_length_async(output_path)
                    return filename, duration
                
                duration = await self.download_audio(url, output_path)
                return filename, duration
        
        tasks = []
        for url in surah_urls:
            # Extract filename from URL
            filename = Path(url).name
            if not filename.endswith(".mp3"):
                filename += ".mp3"
            tasks.append(download_single(url, filename))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        downloaded = {}
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Failed to download audio: {result}")
            else:
                filename, duration = result
                downloaded[filename] = duration
        
        return downloaded
    
    def validate_audio_files(
        self,
        files: List[Path],
        min_duration: float = 0.1,
        max_duration: float = 75.0
    ) -> List[Path]:
        """
        Validate audio files meet duration requirements.
        
        Args:
            files: List of audio file paths
            min_duration: Minimum duration in minutes
            max_duration: Maximum duration in minutes
            
        Returns:
            List of valid audio file paths
        """
        valid_files = []
        for file_path in files:
            try:
                duration = self.get_audio_length(file_path)
                if min_duration <= duration <= max_duration:
                    valid_files.append(file_path)
                else:
                    self.logger.warning(
                        f"Audio file {file_path} has invalid duration: {duration}m "
                        f"(expected {min_duration}-{max_duration}m)"
                    )
                    if file_path.exists():
                        file_path.unlink()
            except Exception as e:
                self.logger.error(f"Failed to validate {file_path}: {e}")
        
        return valid_files
