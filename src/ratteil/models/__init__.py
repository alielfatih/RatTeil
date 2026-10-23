"""
Models for RatTeil application.
"""

from ratteil.models.surah import SurahInfo
from ratteil.models.reciter import Reciter
from ratteil.models.stream import StreamConfig, StreamDetails
from ratteil.models.auth import AuthCredentials, OAuthToken

__all__ = [
    "SurahInfo",
    "Reciter",
    "StreamConfig",
    "StreamDetails",
    "AuthCredentials",
    "OAuthToken",
]
