"""
Authentication models for RatTeil application.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json


@dataclass
class OAuthToken:
    """
    OAuth 2.0 token information.
    
    Attributes:
        access_token: The access token
        refresh_token: The refresh token (optional)
        token_type: Type of token (e.g., Bearer)
        expires_in: Seconds until token expires
        scope: Scope of the token
        issued_at: When the token was issued
        expires_at: When the token expires
    """
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = ""
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps."""
        if self.issued_at is None:
            self.issued_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.issued_at + timedelta(seconds=self.expires_in)
    
    def is_expired(self) -> bool:
        """Check if token has expired."""
        if self.expires_at:
            return datetime.now() >= self.expires_at
        return True
    
    def get_authorization_header(self) -> str:
        """Get Authorization header value."""
        return f"{self.token_type} {self.access_token}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "scope": self.scope,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
    
    def to_json(self) -> str:
        """Convert token to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> "OAuthToken":
        """Create OAuthToken from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthToken":
        """Create OAuthToken from dictionary."""
        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 3600),
            scope=data.get("scope", ""),
            issued_at=datetime.fromisoformat(data["issued_at"]) if data.get("issued_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
        )


@dataclass
class AuthCredentials:
    """
    Authentication credentials for a service.
    
    Attributes:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        access_token: Current access token
        refresh_token: Current refresh token
        scopes: List of OAuth scopes
        token_expiry: When the token expires
    """
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    scopes: list = field(default_factory=list)
    token_expiry: Optional[datetime] = None
    
    def has_credentials(self) -> bool:
        """Check if credentials are available."""
        return bool(self.client_id and self.client_secret)
    
    def has_token(self) -> bool:
        """Check if access token is available."""
        return bool(self.access_token)
    
    def is_token_expired(self) -> bool:
        """Check if token has expired."""
        if self.token_expiry:
            return datetime.now() >= self.token_expiry
        return not self.has_token()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert credentials to dictionary."""
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "scopes": self.scopes,
            "token_expiry": self.token_expiry.isoformat() if self.token_expiry else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthCredentials":
        """Create AuthCredentials from dictionary."""
        return cls(
            client_id=data.get("client_id"),
            client_secret=data.get("client_secret"),
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            scopes=data.get("scopes", []),
            token_expiry=datetime.fromisoformat(data["token_expiry"]) if data.get("token_expiry") else None,
        )


@dataclass
class YouTubeCredentials(AuthCredentials):
    """YouTube-specific authentication credentials."""
    pass


@dataclass
class FacebookCredentials(AuthCredentials):
    """Facebook-specific authentication credentials."""
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    page_id: Optional[str] = None
