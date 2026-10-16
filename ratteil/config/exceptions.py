"""Custom exceptions for RatTeil application."""


class RatTeilError(Exception):
    """Base exception for all RatTeil errors."""
    pass


class ConfigurationError(RatTeilError):
    """Raised when there's a configuration issue."""
    pass


class DownloadError(RatTeilError):
    """Raised when download operations fail."""
    pass


class StreamError(RatTeilError):
    """Raised when streaming operations fail."""
    pass


class ValidationError(RatTeilError):
    """Raised when validation fails."""
    pass


class AudioMergeError(RatTeilError):
    """Raised when audio merging fails."""
    pass


class YouTubeError(RatTeilError):
    """Raised when YouTube API operations fail."""
    pass
