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
        return {
            1: 'akdr', 2: 'jbreen', 3: '3siri', 4: 'shatri', 5: 'ajm',
            6: 'hawashi', 7: 'saud', 8: 'saber', 9: 'ahmad_nu', 10: 'akrm',
            11: '3zazi', 12: 'abkr', 13: 'alzain', 14: 'qari', 15: 'omran',
            16: 'koshi', 17: 'twfeeq', 18: 'jamal', 19: 'hamad', 20: 'jleel',
            21: 'qht', 22: 'kafi', 23: 'whabi', 24: 'tnjy', 25: 'hamza',
            26: 'ifrad', 27: 'bl3', 28: 'zakariya', 29: 's_gmd', 30: 'shur',
            31: 'shl', 32: 'zaki', 33: 'sami_hsn', 34: 'sami_dosr', 35: 'sayed',
            36: 'shaban', 37: 'taher', 38: 'hkm', 39: 'sahood', 40: 'tlb',
            41: 'habdan', 42: 's_bud', 43: 'salah_hashim_m', 44: 'bu_khtr', 45: 'ryan',
            46: 'thubti', 47: 'bari', 48: 'basit', 49: 'sds', 50: 'a_ahmed',
            51: 'zahrani', 52: 'brmi', 53: 'buajan', 54: 'mtrod', 55: 'bsfr',
            56: 'kyat', 57: 'jhn', 58: 'gulan', 59: 'soufi', 60: 'mohsin_harthi',
            61: 'qasm', 62: 'askr', 63: 'obk', 64: 'kanakeri', 65: 'wdod',
            66: 'arkani', 67: 'abo_hashim', 68: 'hthfi', 70: 'a_jbr', 71: 'hajjaj',
            72: 'hafz', 73: 'omar_warsh', 74: 'frs_a', 75: 'fahad_otibi',
            76: 'kndri', 77: 'fawaz', 78: 'lafi', 79: 'qtm', 80: 'nabil',
            81: 'namh', 82: 'hani', 83: 'dlami', 84: 'waleed', 85: 'yasser',
            86: 'qurashi', 87: 'fyl', 88: 'mzroyee', 89: 'yahya', 90: 'yousef',
            91: 'majd_onazi', 92: 'shaibat', 93: 'maher', 94: 'earawi', 95: 'braak',
            96: 'tblawi', 97: 'lhdan', 98: 'mhsny', 99: 'ayyoub2', 100: 'shah',
            101: 'jbrl', 102: 'minsh', 103: 'm_krm', 104: 'abdullah', 105: 'husr',
            106: 'bna', 107: 'afs', 108: 'mustafa', 109: 'lahoni', 110: 'ra3ad',
            111: 'muamr', 113: 'zaml', 114: 'shaksh', 115: 'monshed', 116: 'sheimy',
            117: 'salamah', 120: 'mohna', 121: 'a_klb', 122: 'bilal', 123: 'alshaik',
            124: 'hatem', 125: 'jormy', 126: 'mrifai', 127: 'obaid', 128: 'wasel',
            129: 'ibrahim_dosri', 130: 'jaman', 139: 'malaysia', 140: 'noah',
            141: 'zilaie', 142: 'harthi', 143: 'rashad', 145: 'trablsi',
            149: 'ahmad_huth', 150: 'khan', 151: 'dgsh', 152: 'dokali', 153: 'wishear',
            154: 'fateh', 155: 'tareq', 157: 'balilah', 158: 'shoraimy', 159: 'wdee3',
            160: 'kurdi', 162: 'aloosi', 163: 'ghamdi', 164: 'shakoor', 165: 'm_arkani',
            166: 'm_qari', 167: 'rami', 168: 'hazza', 169: 'a_majed', 170: 'salman',
            171: 'refat', 172: 'mousa', 173: 'khalf', 174: 'mansor', 175: 'musali',
            176: 'sharekh', 177: 'alosfor', 181: 'swlim', 182: 'islam',
            184: 'bader', 186: 'hitham', 187: 'nasser_almajed', 188: 'shaheen',
            189: 'bukheet', 190: 'saad', 191: 'nufais', 192: 'darweez',
            197: 'abdulazizasiri', 198: 'souilass', 199: 'deban', 200: 'kamel',
            201: 'peshawa', 206: 'okasha', 208: 'h_dukhain', 221: 'sneineh',
            222: 'qeniwa', 223: 'm_abdelhakam', 227: 'm_sayed', 228: 'a_swaiyd',
            229: 'a_binaoun', 230: 'a_binhameed', 231: 'nourin_siddig',
            232: 'a_bukhari', 233: 'a_turki', 234: 'mukhtar_haj', 235: 'a_abdl',
            236: 'm_akri', 237: 'a_maasaraawi', 238: 'i_kshidan', 239: 'h_abudalal',
            240: 'f_khamery', 241: 's_hashemi', 242: 'kh_mohammadi', 243: 'shamrani',
            245: 's_sadeiq', 246: 'h_saleh', 247: 'a_alshahhat', 248: 'i_sanankoua',
            249: 'h_baqai', 250: 's_alquraishi', 251: 'f_hajry', 252: 'a_alemadi',
            253: 'a_alaskar', 285: 'a_alhazmi', 301: 'a_sheim'
        }
    
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
