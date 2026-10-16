"""Audio service for merging and processing audio files."""

import subprocess
from pathlib import Path
from typing import List, Optional

from ratteil.config import get_settings, AudioMergeError
from ratteil.models.stream import StreamFile


class AudioService:
    """Service for handling audio file operations."""
    
    def __init__(self):
        """Initialize the audio service."""
        self.settings = get_settings()
    
    def merge_audios(
        self,
        input_paths: List[Path],
        output_path: Path,
        format: Optional[str] = None,
        bitrate: Optional[str] = None,
    ) -> Path:
        """Merge multiple audio files into one.
        
        Args:
            input_paths: List of input audio file paths
            output_path: Path for the output merged file
            format: Output format (default from settings)
            bitrate: Output bitrate (default from settings)
            
        Returns:
            Path to the merged audio file
            
        Raises:
            AudioMergeError: If merging fails
        """
        if not input_paths:
            raise AudioMergeError("No input files provided for merging")
        
        format = format or self.settings.AUDIO_FORMAT
        bitrate = bitrate or self.settings.AUDIO_BITRATE
        
        # Create input file list
        input_file = output_path.parent / "input_list.txt"
        with open(input_file, 'w') as f:
            for path in input_paths:
                f.write(f"file '{path}'\n")
        
        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(input_file),
            "-c", "copy",
            "-b:a", bitrate,
            str(output_path),
        ]
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            return output_path
        except subprocess.CalledProcessError as e:
            raise AudioMergeError(
                f"Failed to merge audio files: {e.stderr}"
            ) from e
        finally:
            if input_file.exists():
                input_file.unlink()
    
    def get_duration(self, audio_path: Path) -> float:
        """Get duration of an audio file in seconds.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration in seconds
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ]
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as e:
            raise AudioMergeError(
                f"Failed to get duration for {audio_path}: {e}"
            ) from e
    
    def convert_format(
        self,
        input_path: Path,
        output_path: Path,
        format: str = "mp3",
        bitrate: str = "192k",
    ) -> Path:
        """Convert audio file to specified format.
        
        Args:
            input_path: Path to the input audio file
            output_path: Path for the output file
            format: Target format
            bitrate: Target bitrate
            
        Returns:
            Path to the converted file
        """
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-c:a", "libmp3lame" if format == "mp3" else "copy",
            "-b:a", bitrate,
            str(output_path),
        ]
        
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            return output_path
        except subprocess.CalledProcessError as e:
            raise AudioMergeError(
                f"Failed to convert audio file: {e.stderr}"
            ) from e
    
    def prepare_stream_files(
        self,
        audio_paths: List[Path],
        output_dir: Optional[Path] = None,
    ) -> List[StreamFile]:
        """Prepare audio files for streaming.
        
        Args:
            audio_paths: List of audio file paths
            output_dir: Optional output directory
            
        Returns:
            List of StreamFile objects
        """
        output_dir = output_dir or (self.settings.STREAM_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        stream_files = []
        for i, audio_path in enumerate(audio_paths):
            # Extract metadata from filename (format: {surah_id}_{surah_name}.mp3)
            filename = audio_path.stem
            parts = filename.split('_')
            surah_id = int(parts[0]) if parts else 0
            
            # Create stream file
            stream_file = StreamFile(
                path=str(audio_path),
                surah_id=surah_id,
                reciter_id="unknown",  # Will be updated
                duration=self.get_duration(audio_path),
                order=i,
            )
            stream_files.append(stream_file)
        
        return stream_files
