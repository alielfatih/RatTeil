"""
Base authentication service for RatTeil application.

This module provides the base classes and interfaces for authentication services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol, runtime_checkable
from pathlib import Path
import asyncio

from ratteil.models.auth import OAuthToken, AuthCredentials
from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import AuthError, TokenExpiredError, InvalidTokenError


class AuthProvider:
    """Enum-like class for authentication providers."""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"


@runtime_checkable
class AuthServiceProtocol(Protocol):
    """Protocol for authentication services."""
    
    @abstractmethod
    async def authenticate(self) -> OAuthToken:
        """Authenticate and return access token."""
        ...
    
    @abstractmethod
    async def get_token(self) -> OAuthToken:
        """Get current access token, refreshing if necessary."""
        ...
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token using refresh token."""
        ...
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        ...
    
    @abstractmethod
    async def revoke_token(self) -> bool:
        """Revoke current token."""
        ...


class BaseAuthService(ABC):
    """
    Base class for authentication services.
    
    Provides common functionality for all authentication services.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the authentication service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or get_settings()
        self._token: Optional[OAuthToken] = None
        self._credentials: Optional[AuthCredentials] = None
    
    @property
    def provider(self) -> str:
        """Get the provider name."""
        return self.__class__.__name__.replace("AuthService", "").lower()
    
    @abstractmethod
    async def authenticate(self) -> OAuthToken:
        """
        Authenticate and return access token.
        
        This method should implement the authentication flow for the specific
        provider (device flow, service account, etc.).
        
        Returns:
            OAuthToken: The authentication token
        """
        ...
    
    @abstractmethod
    async def get_token(self) -> OAuthToken:
        """
        Get current access token, refreshing if necessary.
        
        Returns:
            OAuthToken: The current access token
        """
        ...
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            OAuthToken: The new access token
        """
        ...
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        if self._token is None:
            return False
        return not self._token.is_expired()
    
    async def revoke_token(self) -> bool:
        """
        Revoke current token.
        
        Returns:
            bool: True if token was revoked, False otherwise
        """
        self._token = None
        self._credentials = None
        return True
    
    def get_token_sync(self) -> OAuthToken:
        """
        Get current access token synchronously.
        
        This is a convenience method for synchronous code.
        
        Returns:
            OAuthToken: The current access token
        """
        if self._token is None or self._token.is_expired():
            # Run async get_token in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                self._token = loop.run_until_complete(self.get_token())
            finally:
                loop.close()
        return self._token
    
    def ensure_authenticated(self) -> None:
        """
        Ensure the service is authenticated.
        
        Raises:
            AuthError: If not authenticated
        """
        if not self.is_authenticated():
            raise AuthError(f"Not authenticated for {self.provider}", provider=self.provider)
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for authenticated requests.
        
        Returns:
            Dictionary of HTTP headers
        """
        token = self.get_token_sync()
        return {
            "Authorization": token.get_authorization_header(),
            "Content-Type": "application/json",
        }


class TokenManager:
    """
    Manages OAuth tokens for authentication services.
    
    Provides token storage, retrieval, and refresh functionality.
    """
    
    def __init__(self, token_dir: Optional[Path] = None, provider: str = ""):
        """
        Initialize the token manager.
        
        Args:
            token_dir: Directory to store tokens
            provider: Name of the provider
        """
        self.token_dir = token_dir or Path.home() / ".ratteil" / "tokens"
        self.provider = provider
        self._token_path = self.token_dir / f"{provider}_token.json"
        
        # Create directory if it doesn't exist
        self.token_dir.mkdir(parents=True, exist_ok=True)
    
    def save_token(self, token: OAuthToken) -> bool:
        """
        Save token to file.
        
        Args:
            token: The token to save
            
        Returns:
            bool: True if token was saved successfully
        """
        try:
            self._token_path.write_text(token.to_json())
            return True
        except Exception as e:
            print(f"Failed to save token: {e}")
            return False
    
    def load_token(self) -> Optional[OAuthToken]:
        """
        Load token from file.
        
        Returns:
            OAuthToken: The loaded token, or None if not found
        """
        if not self._token_path.exists():
            return None
        
        try:
            import json
            data = json.loads(self._token_path.read_text())
            return OAuthToken.from_dict(data)
        except Exception as e:
            print(f"Failed to load token: {e}")
            return None
    
    def delete_token(self) -> bool:
        """
        Delete token file.
        
        Returns:
            bool: True if token was deleted successfully
        """
        if self._token_path.exists():
            self._token_path.unlink()
            return True
        return False


class DeviceFlowMixin:
    """
    Mixin class for device flow authentication.
    
    Provides common functionality for OAuth 2.0 device flow.
    """
    
    async def perform_device_flow(self, 
                                  client_id: str,
                                  scope: str,
                                  auth_url: str,
                                  token_url: str) -> OAuthToken:
        """
        Perform OAuth 2.0 device flow authentication.
        
        Args:
            client_id: OAuth client ID
            scope: Requested scope
            auth_url: Authorization endpoint URL
            token_url: Token endpoint URL
            
        Returns:
            OAuthToken: The access token
        """
        import aiohttp
        import webbrowser
        
        # Step 1: Get device code
        device_code_url = f"{auth_url}/device/code"
        
        async with aiohttp.ClientSession() as session:
            # Request device code
            data = {
                "client_id": client_id,
                "scope": scope,
            }
            
            async with session.post(device_code_url, data=data) as response:
                if response.status != 200:
                    raise AuthError(
                        f"Failed to get device code: {response.status}",
                        provider=self.provider
                    )
                
                device_data = await response.json()
                device_code = device_data.get("device_code")
                user_code = device_data.get("user_code")
                verification_url = device_data.get("verification_url")
                expires_in = device_data.get("expires_in", 900)
                interval = device_data.get("interval", 5)
            
            # Step 2: Display user code and verification URL
            print(f"\n{self.provider.upper()} Authentication")
            print("=" * 50)
            print(f"Please visit: {verification_url}")
            print(f"Enter code: {user_code}")
            print("=" * 50)
            
            # Optionally open browser
            try:
                webbrowser.open(verification_url)
            except Exception:
                pass
            
            # Step 3: Poll for token
            import time
            start_time = time.time()
            
            while time.time() - start_time < expires_in:
                await asyncio.sleep(interval)
                
                token_data = {
                    "client_id": client_id,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                }
                
                async with session.post(token_url, data=token_data) as response:
                    if response.status == 200:
                        token_response = await response.json()
                        return OAuthToken(
                            access_token=token_response.get("access_token"),
                            refresh_token=token_response.get("refresh_token"),
                            token_type=token_response.get("token_type", "Bearer"),
                            expires_in=token_response.get("expires_in", 3600),
                            scope=token_response.get("scope", ""),
                        )
                    elif response.status == 400:
                        # Check for authorization_pending
                        error_data = await response.json()
                        if error_data.get("error") != "authorization_pending":
                            raise AuthError(
                                f"Token request failed: {error_data.get('error_description', 'Unknown error')}",
                                provider=self.provider
                            )
            
            # Timeout
            raise AuthError(
                "Device flow authentication timed out",
                provider=self.provider
            )
