"""
Repositories for RatTeil application.
"""

from ratteil.repositories.protocols import (
    SurahRepositoryProtocol,
    ReciterRepositoryProtocol,
    AudioRepositoryProtocol,
    StreamRepositoryProtocol,
    ResourceRepositoryProtocol,
)
from ratteil.repositories.surah_repository import SurahRepository
from ratteil.repositories.reciter_repository import ReciterRepository

__all__ = [
    "SurahRepositoryProtocol",
    "ReciterRepositoryProtocol",
    "AudioRepositoryProtocol",
    "StreamRepositoryProtocol",
    "ResourceRepositoryProtocol",
    "SurahRepository",
    "ReciterRepository",
]
