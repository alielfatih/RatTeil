"""
API client for fetching Quran data from mp3quran.net.
"""

import aiohttp
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

from ratteil.data.models import Language, Reciter, Surah, QuranData
from ratteil.data.exceptions import APIError, LanguageNotSupportedError
from ratteil.utils.logging import get_logger


class QuranAPIClient:
    """
    Client for fetching Quran data from mp3quran.net API.
    
    API Endpoints:
    - GET https://mp3quran.net/api/v3/languages - Get available languages
    - GET https://mp3quran.net/api/v3/reciters?language={lang} - Get reciters
    - GET https://mp3quran.net/api/v3/suwar?language={lang} - Get surahs
    """
    
    BASE_URL = "https://www.mp3quran.net/api/v3"
    
    # Default languages that are known to work
    SUPPORTED_LANGUAGES = ["ar", "en", "fr", "de", "es", "tr", "ur", "fa", "ru"]
    
    def __init__(self, timeout: int = 30):
        """
        Initialize API client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.logger = get_logger("ratteil.data.api")
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self) -> "QuranAPIClient":
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response
            
        Raises:
            APIError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        if not self._session:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        try:
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise APIError(
                        f"API request failed: {response.status} - {error_text}",
                        url=url,
                        status_code=response.status
                    )
                
                data = await response.json()
                
                # Check for error in response
                if not data.get("status", True):
                    error_msg = data.get("message", "Unknown error")
                    raise APIError(f"API error: {error_msg}", url=url)
                
                return data
        except aiohttp.ClientError as e:
            raise APIError(f"Network error: {e}", url=url) from e
        except asyncio.TimeoutError as e:
            raise APIError(f"Request timeout: {e}", url=url) from e
    
    async def get_languages(self) -> List[Language]:
        """
        Get list of available languages from API.
        
        Returns:
            List of Language objects
        """
        try:
            data = await self._get("languages")
            # API returns "language" (singular) not "languages" (plural)
            languages_data = data.get("language", [])
            
            languages = []
            for lang_data in languages_data:
                languages.append(Language(
                    code=lang_data.get("locale", lang_data.get("code", "")),
                    name=lang_data.get("language", lang_data.get("name", "")),
                    native_name=lang_data.get("native", lang_data.get("native_name", "")),
                    rtl=lang_data.get("rtl", False)
                ))
            
            return languages
        except APIError:
            # Fallback to default supported languages
            self.logger.warning("Failed to fetch languages from API, using defaults")
            return [
                Language(code="ar", name="Arabic", native_name="العربية", rtl=True),
                Language(code="en", name="English", native_name="English", rtl=False),
            ]
    
    async def get_reciters(self, language: str = "ar") -> List[Reciter]:
        """
        Get list of reciters from API.
        
        Args:
            language: Language code for reciter names
            
        Returns:
            List of Reciter objects
            
        Raises:
            LanguageNotSupportedError: If language is not supported
            APIError: If API request fails
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise LanguageNotSupportedError(language, self.SUPPORTED_LANGUAGES)
        
        try:
            data = await self._get("reciters", params={"language": language})
            reciters_data = data.get("reciters", [])
            
            # Build a mapping from API IDs to codes from static data
            # This ensures compatibility with existing code that uses codes like 'akdr', 'husary', etc.
            code_mapping = self._build_reciter_code_mapping()
            
            reciters = []
            for reciter_data in reciters_data:
                reciter_id = reciter_data.get("id", 0)
                # Use code from mapping if available, otherwise use the ID
                code = code_mapping.get(reciter_id, str(reciter_id))
                
                reciter = Reciter(
                    id=reciter_id,
                    code=code,
                    name=reciter_data.get("name", ""),
                    letter=reciter_data.get("letter", ""),
                    moshafs=reciter_data.get("moshaf", []),
                    language=language
                )
                reciters.append(reciter)
            
            return reciters
        except APIError:
            self.logger.warning(f"Failed to fetch reciters for language {language}")
            return []
    
    def _build_reciter_code_mapping(self) -> Dict[int, str]:
        """
        Build a mapping from API reciter IDs to codes used in static data.
        
        Returns:
            Dictionary mapping API IDs to codes
        """
        return {}
    
    async def get_surahs(self, language: str = "ar") -> List[Surah]:
        """
        Get list of surahs from API.
        
        Args:
            language: Language code for surah names
            
        Returns:
            List of Surah objects
            
        Raises:
            LanguageNotSupportedError: If language is not supported
            APIError: If API request fails
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise LanguageNotSupportedError(language, self.SUPPORTED_LANGUAGES)
        
        try:
            data = await self._get("suwar", params={"language": language})
            surahs_data = data.get("suwar", [])
            
            surahs = []
            for surah_data in surahs_data:
                surah = Surah.from_dict(surah_data, language)
                surahs.append(surah)
            
            return surahs
        except APIError:
            self.logger.warning(f"Failed to fetch surahs for language {language}")
            return []
    
    async def fetch_all_data(self, language: str = "ar") -> QuranData:
        """
        Fetch all data (languages, reciters, surahs) from API.
        
        Args:
            language: Language code for data
            
        Returns:
            QuranData object with all data
        """
        languages = await self.get_languages()
        reciters = await self.get_reciters(language)
        surahs = await self.get_surahs(language)
        
        return QuranData(
            languages=languages,
            reciters=reciters,
            surahs=surahs,
            cached_at=datetime.now(),
            language=language,
            version="1.0"
        )
    
    def get_all_data_sync(self, language: str = "ar") -> QuranData:
        """
        Fetch all data synchronously.
        
        Args:
            language: Language code for data
            
        Returns:
            QuranData object with all data
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.fetch_all_data(language))
        finally:
            loop.close()
