"""Data models for RatTeil application."""

from .surah import Surah, SurahInfo
from .reciter import Reciter, Moshaf
from .stream import StreamDetails, StreamFile

__all__ = [
    "Surah",
    "SurahInfo",
    "Reciter",
    "Moshaf",
    "StreamDetails",
    "StreamFile",
]
