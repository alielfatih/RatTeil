"""
Repository protocols (interfaces) for RatTeil application.

These protocols define the interface that all repositories must implement,
enabling dependency injection and easier testing.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator, Protocol, runtime_checkable
from pathlib import Path

from ratteil.models.surah import SurahInfo
from ratteil.models.reciter import Reciter


@runtime_checkable
class SurahRepositoryProtocol(Protocol):
    """Protocol for Surah repository."""
    
    @abstractmethod
    def get_surah(self, surah_id: int | str, reciter_id: int | str, moshaf_type: int | str) -> SurahInfo:
        """Get a single surah by ID, reciter ID, and moshaf type."""
        ...
    
    @abstractmethod
    def get_surahs(self, surah_ids: List[int | str], reciter_id: int | str, moshaf_type: int | str) -> List[SurahInfo]:
        """Get multiple surahs by IDs, reciter ID, and moshaf type."""
        ...
    
    @abstractmethod
    def list_all_surahs(self) -> Dict[str, Dict[str, Any]]:
        """List all available surahs."""
        ...
    
    @abstractmethod
    def search_surahs(self, query: str, limit: int = 10) -> List[SurahInfo]:
        """Search surahs by name or other criteria."""
        ...
    
    @abstractmethod
    def get_surah_audio_url(self, surah: SurahInfo) -> str:
        """Get the audio URL for a surah."""
        ...


@runtime_checkable
class ReciterRepositoryProtocol(Protocol):
    """Protocol for Reciter repository."""
    
    @abstractmethod
    def get_reciter(self, reciter_id: int | str) -> Reciter:
        """Get a single reciter by ID."""
        ...
    
    @abstractmethod
    def get_reciters(self, reciter_ids: List[int | str]) -> List[Reciter]:
        """Get multiple reciters by IDs."""
        ...
    
    @abstractmethod
    def list_all_reciters(self) -> Dict[str, Dict[str, Any]]:
        """List all available reciters."""
        ...
    
    @abstractmethod
    def get_reciters_with_multi_moshafs(self) -> List[int | str]:
        """Get list of reciters with multiple moshafs."""
        ...
    
    @abstractmethod
    def search_reciters(self, query: str, limit: int = 10) -> List[Reciter]:
        """Search reciters by name."""
        ...
    
    @abstractmethod
    def get_available_reciters_list(self) -> List[str]:
        """Get formatted list of available reciters."""
        ...


@runtime_checkable
class AudioRepositoryProtocol(Protocol):
    """Protocol for Audio repository (file system operations)."""
    
    @abstractmethod
    def download_audio(self, url: str, output_path: Path) -> Path:
        """Download audio file from URL."""
        ...
    
    @abstractmethod
    async def download_audio_async(self, url: str, output_path: Path) -> Path:
        """Download audio file from URL asynchronously."""
        ...
    
    @abstractmethod
    def get_audio_length(self, file_path: Path) -> float:
        """Get audio file duration in minutes."""
        ...
    
    @abstractmethod
    async def get_audio_length_async(self, file_path: Path) -> float:
        """Get audio file duration in minutes asynchronously."""
        ...
    
    @abstractmethod
    def merge_audios(self, audio_files: List[Path], output_path: Path) -> Path:
        """Merge multiple audio files into one."""
        ...
    
    @abstractmethod
    async def merge_audios_async(self, audio_files: List[Path], output_path: Path) -> Path:
        """Merge multiple audio files into one asynchronously."""
        ...
    
    @abstractmethod
    def list_audio_files(self, directory: Path) -> List[Path]:
        """List all audio files in directory."""
        ...
    
    @abstractmethod
    def delete_audio_file(self, file_path: Path) -> bool:
        """Delete an audio file."""
        ...


@runtime_checkable
class StreamRepositoryProtocol(Protocol):
    """Protocol for Stream repository."""
    
    @abstractmethod
    def create_stream(self, title: str, description: str, platform: str) -> Dict[str, Any]:
        """Create a new stream on the specified platform."""
        ...
    
    @abstractmethod
    async def create_stream_async(self, title: str, description: str, platform: str) -> Dict[str, Any]:
        """Create a new stream on the specified platform asynchronously."""
        ...
    
    @abstractmethod
    def start_stream(self, stream_id: str, platform: str) -> bool:
        """Start a stream."""
        ...
    
    @abstractmethod
    def stop_stream(self, stream_id: str, platform: str) -> bool:
        """Stop a stream."""
        ...
    
    @abstractmethod
    def get_stream_info(self, stream_id: str, platform: str) -> Dict[str, Any]:
        """Get information about a stream."""
        ...


@runtime_checkable
class ResourceRepositoryProtocol(Protocol):
    """Protocol for managing application resources."""
    
    @abstractmethod
    def ensure_resources_initialized(self, base_path: Path) -> None:
        """Ensure all required resource directories exist."""
        ...
    
    @abstractmethod
    def get_resource_path(self, resource_type: str) -> Path:
        """Get path for a specific resource type."""
        ...
    
    @abstractmethod
    def copy_resource(self, source: Path, destination: Path) -> bool:
        """Copy a resource from source to destination."""
        ...
    
    @abstractmethod
    def list_resources(self, resource_type: str) -> List[Path]:
        """List all resources of a specific type."""
        ...
