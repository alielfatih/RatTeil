"""Data repositories for RatTeil application."""

from .reciter_repository import ReciterRepository, LocalReciterRepository
from .surah_repository import SurahRepository, LocalSurahRepository

__all__ = [
    "ReciterRepository",
    "LocalReciterRepository",
    "SurahRepository",
    "LocalSurahRepository",
]
