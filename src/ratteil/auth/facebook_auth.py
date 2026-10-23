"""
Facebook authentication service for RatTeil application.

This module provides authentication for Facebook Graph API.
"""

import aiohttp
from typing import Optional, Dict, Any
from pathlib import Path

from ratteil.models.auth import OAuthToken, FacebookCredentials
from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import AuthError, TokenExpiredError, InvalidTokenError
from ratteil.auth.base import BaseAuthService, TokenManager
from ratteil.utils.logging import get_logger


class FacebookAuthService(BaseAuthService):
    """
    Facebook Graph API authentication service.
    
    Uses access tokens for authentication.
    """
    
    FACEBOOK_GRAPH_API = "https://graph.facebook.com/v20.0"
    FACEBOOK_OAUTH_URL = "https://www.facebook.com/v20.0/dialog/oauth"
    FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v20.0/oauth/access_token"
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize Facebook authentication service.
        
        Args:
            settings: Application settings
        """
        super().__init__(settings)
        self.logger = get_logger(f"ratteil.auth.{self.provider}")
        self.token_manager = TokenManager(provider="facebook")
        
        # Load existing token
        self._token = self.token_manager.load_token()
    
    async def authenticate(self) -> OAuthToken:
        """
        Authenticate using Facebook access token.
        
        For Facebook, we typically use a pre-configured access token
        rather than implementing a full OAuth flow.
        
        Returns:
            OAuthToken: The access token
        """
        if not self.settings.facebook_access_token:
            raise AuthError(
                "Facebook access token not configured. "
                "Please set FACEBOOK_ACCESS_TOKEN environment variable.",
                provider=self.provider
            )
        
        # Validate token
        if not await self._validate_token(self.settings.facebook_access_token):
            raise AuthError(
                "Invalid Facebook access token",
                provider=self.provider
            )
        
        # Create token object
        token = OAuthToken(
            access_token=self.settings.facebook_access_token,
            token_type="Bearer",
            expires_in=3600,  # Facebook tokens typically expire in 1-2 hours
            scope=" ".join(self.settings.get_facebook_scopes()),
        )
        
        self._token = token
        self.token_manager.save_token(token)
        
        self.logger.info("Facebook authentication successful")
        return token
    
    async def get_token(self) -> OAuthToken:
        """
        Get current access token.
        
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
        Refresh access token.
        
        Note: Facebook access tokens are typically long-lived and don't
        support the standard refresh token flow. This method is provided
        for compatibility but may not work for all token types.
        
        Args:
            refresh_token: The refresh token (not typically used for Facebook)
            
        Returns:
            OAuthToken: The new access token
        """
        # Facebook doesn't typically support refresh tokens for access tokens
        # Just return the current token
        return await self.get_token()
    
    async def _validate_token(self, token: str) -> bool:
        """
        Validate Facebook access token.
        
        Args:
            token: The access token to validate
            
        Returns:
            bool: True if token is valid
        """
        try:
            url = f"{self.FACEBOOK_GRAPH_API}/debug_token"
            params = {
                "input_token": token,
                "access_token": f"{token}|{self.settings.facebook_app_secret}",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("is_valid", False)
        except Exception as e:
            self.logger.warning(f"Failed to validate Facebook token: {e}")
        
        return False
    
    async def get_credentials(self) -> FacebookCredentials:
        """
        Get Facebook credentials.
        
        Returns:
            FacebookCredentials: The credentials
        """
        token = await self.get_token()
        return FacebookCredentials(
            client_id=None,
            client_secret=None,
            access_token=token.access_token,
            refresh_token=None,
            scopes=self.settings.get_facebook_scopes(),
            app_id=self.settings.facebook_page_id,
            app_secret=self.settings.facebook_app_secret,
            page_id=self.settings.facebook_page_id,
        )
    
    async def get_page_info(self, page_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a Facebook page.
        
        Args:
            page_id: The page ID (defaults to configured page)
            
        Returns:
            Dictionary containing page information
        """
        token = await self.get_token()
        page_id = page_id or self.settings.facebook_page_id
        
        if not page_id:
            raise AuthError(
                "Facebook page ID not configured",
                provider=self.provider
            )
        
        url = f"{self.FACEBOOK_GRAPH_API}/{page_id}"
        params = {
            "access_token": token.access_token,
            "fields": "id,name,access_token",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise AuthError(
                        f"Failed to get page info: {error_data.get('error', {}).get('message', 'Unknown error')}",
                        provider=self.provider
                    )
    
    async def create_live_stream(self, title: str, description: str) -> Dict[str, Any]:
        """
        Create a Facebook Live stream.
        
        Args:
            title: Stream title
            description: Stream description
            
        Returns:
            Dictionary containing stream information
        """
        token = await self.get_token()
        page_id = self.settings.facebook_page_id
        
        if not page_id:
            raise AuthError(
                "Facebook page ID not configured",
                provider=self.provider
            )
        
        url = f"{self.FACEBOOK_GRAPH_API}/{page_id}/live_videos"
        params = {
            "access_token": f"{token.access_token}|{self.settings.facebook_app_secret}",
            "status": "LIVE_NOW",
            "title": title,
            "description": description,
            "privacy": '{"value": "EVERYONE"}',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise AuthError(
                        f"Failed to create live stream: {error_data.get('error', {}).get('message', 'Unknown error')}",
                        provider=self.provider
                    )
