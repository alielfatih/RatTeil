"""
Authentication module for RatTeil application.

This module provides authentication services for various platforms
using non-GUI (headless) authentication flows.
"""

from ratteil.auth.google_auth import GoogleAuthService, YouTubeAuthService
from ratteil.auth.facebook_auth import FacebookAuthService
from ratteil.auth.base import BaseAuthService, AuthProvider

__all__ = [
    "BaseAuthService",
    "AuthProvider",
    "GoogleAuthService",
    "YouTubeAuthService",
    "FacebookAuthService",
]
