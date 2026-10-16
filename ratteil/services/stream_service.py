"""Stream service for managing streaming operations."""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import List, Optional, Callable, AsyncGenerator

from ratteil.config import get_settings, StreamError
from ratteil.models.surah import Surah, SurahInfo
from ratteil.models.reciter import Reciter
from ratteil.models.stream import StreamDetails, StreamFile, StreamStatus
from ratteil.services.audio_service import AudioService


class StreamService:
    """Service for managing streaming operations."""
    
    def __init__(
        self,
        audio_service: Optional[AudioService] = None,
    ):
        """Initialize the stream service."""
        self.settings = get_settings()
        self.audio_service = audio_service or AudioService()
        self._current_stream: Optional[StreamDetails] = None
    
    def generate_stream_details(
        self,
        surahs: List[Surah],
        reciters: List[Reciter],
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> StreamDetails:
        """Generate stream details from surahs and reciters.
        
        Args:
            surahs: List of surahs to include
            reciters: List of reciters
            title: Optional stream title
            description: Optional stream description
            
        Returns:
            StreamDetails object
        """
        title = title or self.settings.STREAM_TITLE
        description = description or self.settings.STREAM_DESCRIPTION
        
        stream_details = StreamDetails(
            title=title,
            description=description,
        )
        
        # Generate stream files
        order = 0
        for surah in surahs:
            for reciter in reciters:
                # Find audio file for this surah and reciter
                audio_pattern = f"{surah.id:03d}_{surah.name.replace(' ', '_')}_{reciter.id}.mp3"
                audio_files = list(Path(self.settings.AUDIO_DIR).rglob(audio_pattern))
                
                if audio_files:
                    audio_path = audio_files[0]
                    duration = self.audio_service.get_duration(audio_path)
                    
                    stream_file = StreamFile(
                        path=str(audio_path),
                        surah_id=surah.id,
                        reciter_id=reciter.id,
                        duration=duration,
                        order=order,
                    )
                    stream_details.add_file(stream_file)
                    order += 1
        
        return stream_details
    
    def prepare_stream_files(
        self,
        stream_details: StreamDetails,
        output_dir: Optional[Path] = None,
    ) -> List[Path]:
        """Prepare stream files by merging if necessary.
        
        Args:
            stream_details: Stream details to prepare
            output_dir: Optional output directory
            
        Returns:
            List of prepared file paths
        """
        output_dir = output_dir or self.settings.STREAM_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        
        prepared_files = []
        for stream_file in stream_details.stream_files:
            # For now, just use the existing files
            # In the future, we might merge multiple files
            prepared_files.append(Path(stream_file.path))
        
        return prepared_files
    
    def stream_validation(
        self,
        stream_details: StreamDetails,
    ) -> bool:
        """Validate stream details.
        
        Args:
            stream_details: Stream details to validate
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        from ratteil.config import ValidationError
        
        if not stream_details.stream_files:
            raise ValidationError("No files in stream")
        
        if stream_details.total_duration > self.settings.MAX_AUDIO_LENGTH:
            raise ValidationError(
                f"Total duration {stream_details.total_duration}s exceeds "
                f"maximum of {self.settings.MAX_AUDIO_LENGTH}s"
            )
        
        # Check all files exist
        for stream_file in stream_details.stream_files:
            if not Path(stream_file.path).exists():
                raise ValidationError(
                    f"File not found: {stream_file.path}"
                )
        
        return True
    
    def stream(
        self,
        stream_details: StreamDetails,
        on_progress: Optional[Callable[[StreamFile, int, int], None]] = None,
    ) -> None:
        """Stream the prepared files.
        
        This is a placeholder for the actual streaming implementation.
        In practice, this would use FFmpeg to stream to RTMP endpoints.
        
        Args:
            stream_details: Stream details to stream
            on_progress: Optional callback for progress updates
        """
        self.stream_validation(stream_details)
        
        total_files = len(stream_details.stream_files)
        for i, stream_file in enumerate(stream_details.stream_files):
            if on_progress:
                on_progress(stream_file, i + 1, total_files)
            
            # Simulate streaming
            print(f"Streaming file {i + 1}/{total_files}: {stream_file.path}")
        
        stream_details.mark_completed()
    
    async def stream_async(
        self,
        stream_details: StreamDetails,
        on_progress: Optional[Callable[[StreamFile, int, int], None]] = None,
    ) -> AsyncGenerator[StreamFile, None]:
        """Async generator for streaming files.
        
        Args:
            stream_details: Stream details to stream
            on_progress: Optional callback for progress updates
            
        Yields:
            StreamFile objects as they are streamed
        """
        self.stream_validation(stream_details)
        
        total_files = len(stream_details.stream_files)
        for i, stream_file in enumerate(stream_details.stream_files):
            if on_progress:
                on_progress(stream_file, i + 1, total_files)
            
            yield stream_file
            
            # Simulate async streaming delay
            await asyncio.sleep(0.1)
        
        stream_details.mark_completed()
    
    def save_stream_details(
        self,
        stream_details: StreamDetails,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Save stream details to a JSON file.
        
        Args:
            stream_details: Stream details to save
            output_path: Optional output path
            
        Returns:
            Path to the saved file
        """
        output_path = output_path or (
            self.settings.STREAM_DIR / f"{stream_details.title}.json"
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stream_details.to_dict(), f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def load_stream_details(
        self,
        input_path: Path,
    ) -> StreamDetails:
        """Load stream details from a JSON file.
        
        Args:
            input_path: Path to the JSON file
            
        Returns:
            StreamDetails object
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stream_details = StreamDetails(
            title=data.get('title', ''),
            description=data.get('description', ''),
            total_duration=data.get('total_duration', 0.0),
            status=StreamStatus(data.get('status', 'pending')),
        )
        
        for file_data in data.get('files', []):
            stream_file = StreamFile(
                path=file_data.get('path', ''),
                surah_id=file_data.get('surah_id', 0),
                reciter_id=file_data.get('reciter_id', ''),
                duration=file_data.get('duration', 0.0),
                order=file_data.get('order', 0),
            )
            stream_details.stream_files.append(stream_file)
        
        return stream_details
