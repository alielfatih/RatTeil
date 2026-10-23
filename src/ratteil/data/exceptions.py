"""
Exceptions for data management in RatTeil application.
"""

from ratteil.config.exceptions import RatTeilError


class DataError(RatTeilError):
    """Base exception for data-related errors."""
    pass


class APIError(DataError):
    """Exception for API-related errors."""
    
    def __init__(self, message: str, url: str = "", status_code: int = 0):
        self.url = url
        self.status_code = status_code
        super().__init__(message)


class CacheError(DataError):
    """Exception for cache-related errors."""
    pass


class LanguageNotSupportedError(DataError):
    """Exception for unsupported language."""
    
    def __init__(self, language: str, supported: list):
        self.language = language
        self.supported = supported
        super().__init__(
            f"Language '{language}' not supported. "
            f"Supported languages: {', '.join(supported)}"
        )


class ReciterNotFoundError(DataError):
    """Exception for reciter not found."""
    
    def __init__(self, reciter_id: str):
        self.reciter_id = reciter_id
        super().__init__(f"Reciter '{reciter_id}' not found")


class SurahNotFoundError(DataError):
    """Exception for surah not found."""
    
    def __init__(self, surah_id: int):
        self.surah_id = surah_id
        super().__init__(f"Surah {surah_id} not found")
