"""
Google authentication service for RatTeil application.

This module provides non-GUI (headless) authentication for Google/YouTube APIs
using OAuth 2.0 device flow.
"""

import asyncio
import aiohttp
import webbrowser
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

from ratteil.models.auth import OAuthToken, YouTubeCredentials
from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import AuthError, TokenExpiredError, InvalidTokenError
from ratteil.auth.base import BaseAuthService, DeviceFlowMixin, TokenManager
from ratteil.utils.logging import get_logger


class GoogleAuthService(BaseAuthService, DeviceFlowMixin):
    """
    Google OAuth 2.0 authentication service.
    
    Uses device flow for non-GUI authentication.
    """
    
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize Google authentication service.
        
        Args:
            settings: Application settings
        """
        super().__init__(settings)
        self.logger = get_logger(f"ratteil.auth.{self.provider}")
        self.token_manager = TokenManager(provider="google")
        
        # Load existing token
        self._token = self.token_manager.load_token()
    
    async def authenticate(self) -> OAuthToken:
        """
        Authenticate using Google OAuth 2.0 device flow.
        
        Returns:
            OAuthToken: The access token
        """
        if not self.settings.youtube_client_id or not self.settings.youtube_client_secret:
            raise AuthError(
                "Google OAuth credentials not configured. "
                "Please set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET environment variables.",
                provider=self.provider
            )
        
        # Build scope string
        scopes = self.settings.get_youtube_scopes()
        scope = " ".join(scopes)
        
        # Perform device flow
        token = await self.perform_device_flow(
            client_id=self.settings.youtube_client_id,
            scope=scope,
            auth_url=self.GOOGLE_AUTH_URL,
            token_url=self.GOOGLE_TOKEN_URL
        )
        
        # Save token
        self._token = token
        self.token_manager.save_token(token)
        
        self.logger.info("Google authentication successful")
        return token
    
    async def get_token(self) -> OAuthToken:
        """
        Get current access token, refreshing if necessary.
        
        Returns:
            OAuthToken: The current access token
        """
        # Check if we have a valid token
        if self._token and not self._token.is_expired():
            return self._token
        
        # Try to load from file
        self._token = self.token_manager.load_token()
        if self._token and not self._token.is_expired():
            return self._token
        
        # Authenticate
        return await self.authenticate()
    
    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            OAuthToken: The new access token
        """
        if not self.settings.youtube_client_id or not self.settings.youtube_client_secret:
            raise AuthError(
                "Google OAuth credentials not configured.",
                provider=self.provider
            )
        
        data = {
            "client_id": self.settings.youtube_client_id,
            "client_secret": self.settings.youtube_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.GOOGLE_TOKEN_URL, data=data) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise AuthError(
                        f"Failed to refresh token: {error_data.get('error_description', 'Unknown error')}",
                        provider=self.provider
                    )
                
                token_data = await response.json()
                token = OAuthToken(
                    access_token=token_data.get("access_token"),
                    refresh_token=token_data.get("refresh_token", refresh_token),
                    token_type=token_data.get("token_type", "Bearer"),
                    expires_in=token_data.get("expires_in", 3600),
                    scope=token_data.get("scope", ""),
                )
                
                # Save new token
                self._token = token
                self.token_manager.save_token(token)
                
                return token
    
    async def revoke_token(self) -> bool:
        """
        Revoke current token.
        
        Returns:
            bool: True if token was revoked successfully
        """
        if self._token:
            async with aiohttp.ClientSession() as session:
                data = {
                    "token": self._token.access_token,
                }
                async with session.post(self.GOOGLE_REVOKE_URL, data=data) as response:
                    if response.status == 200:
                        self._token = None
                        self.token_manager.delete_token()
                        self.logger.info("Google token revoked")
                        return True
        
        return False


class YouTubeAuthService(GoogleAuthService):
    """
    YouTube-specific authentication service.
    
    Extends GoogleAuthService with YouTube-specific functionality.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize YouTube authentication service.
        
        Args:
            settings: Application settings
        """
        super().__init__(settings)
        self.token_manager = TokenManager(provider="youtube")
        self._token = self.token_manager.load_token()
    
    async def get_credentials(self) -> YouTubeCredentials:
        """
        Get YouTube credentials for API access.
        
        Returns:
            YouTubeCredentials: The credentials
        """
        token = await self.get_token()
        return YouTubeCredentials(
            client_id=self.settings.youtube_client_id,
            client_secret=self.settings.youtube_client_secret,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            scopes=self.settings.get_youtube_scopes(),
        )
    
    async def get_authenticated_client(self) -> Any:
        """
        Get an authenticated YouTube API client.
        
        Returns:
            Authenticated YouTube client
        """
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        token = await self.get_token()
        
        credentials = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=self.GOOGLE_TOKEN_URL,
            client_id=self.settings.youtube_client_id,
            client_secret=self.settings.youtube_client_secret,
            scopes=self.settings.get_youtube_scopes(),
        )
        
        # Build YouTube client
        return build(
            "youtube",
            "v3",
            credentials=credentials,
            static_discovery=False,
        )
