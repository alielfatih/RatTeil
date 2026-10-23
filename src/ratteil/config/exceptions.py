"""
Custom exceptions for RatTeil application.
"""

from typing import Optional, Any


class RatTeilError(Exception):
    """Base exception for all RatTeil errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code or "RATTEIL_ERROR"
        self.details = details
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r}, details={self.details!r})"


class ConfigError(RatTeilError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, missing_field: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message, code="CONFIG_ERROR", details=details)
        self.missing_field = missing_field


class AuthError(RatTeilError):
    """Authentication-related errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message, code="AUTH_ERROR", details=details)
        self.provider = provider


class TokenExpiredError(AuthError):
    """Token expiration error."""
    
    def __init__(self, provider: str, details: Optional[Any] = None):
        super().__init__(f"{provider} token has expired", provider=provider, details=details)
        self.code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthError):
    """Invalid token error."""
    
    def __init__(self, provider: str, token: Optional[str] = None, details: Optional[Any] = None):
        message = f"Invalid {provider} token"
        if token:
            message += f" (token: {token[:8]}...)"
        super().__init__(message, provider=provider, details=details)
        self.code = "INVALID_TOKEN"


class DownloadError(RatTeilError):
    """Download-related errors."""
    
    def __init__(self, message: str, url: Optional[str] = None, path: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message, code="DOWNLOAD_ERROR", details=details)
        self.url = url
        self.path = path


class NetworkError(DownloadError):
    """Network-related errors."""
    
    def __init__(self, message: str = "Network error occurred", url: Optional[str] = None, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message, url=url, details=details)
        self.code = "NETWORK_ERROR"
        self.status_code = status_code


class StreamError(RatTeilError):
    """Streaming-related errors."""
    
    def __init__(self, message: str, platform: Optional[str] = None, stream_id: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message, code="STREAM_ERROR", details=details)
        self.platform = platform
        self.stream_id = stream_id


class ValidationError(RatTeilError):
    """Validation-related errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, details: Optional[Any] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)
        self.field = field
        self.value = value


class FileError(RatTeilError):
    """File-related errors."""
    
    def __init__(self, message: str, path: Optional[str] = None, operation: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message, code="FILE_ERROR", details=details)
        self.path = path
        self.operation = operation


class AudioProcessingError(FileError):
    """Audio processing errors."""
    
    def __init__(self, message: str, path: Optional[str] = None, operation: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message, path=path, operation=operation, details=details)
        self.code = "AUDIO_PROCESSING_ERROR"


class RepositoryError(RatTeilError):
    """Repository-related errors."""
    
    def __init__(self, message: str, repository: Optional[str] = None, operation: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message, code="REPOSITORY_ERROR", details=details)
        self.repository = repository
        self.operation = operation


class NotFoundError(RepositoryError):
    """Resource not found error."""
    
    def __init__(self, resource_type: str, resource_id: Any, repository: Optional[str] = None, details: Optional[Any] = None):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(message, repository=repository, details=details)
        self.code = "NOT_FOUND"
        self.resource_type = resource_type
        self.resource_id = resource_id
