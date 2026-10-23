"""
Facebook service for RatTeil application.

Provides Facebook Live streaming functionality.
"""

from typing import Optional, Dict, Any
from pathlib import Path

from ratteil.config.settings import Settings, get_settings
from ratteil.auth.facebook_auth import FacebookAuthService
from ratteil.utils.logging import get_logger


class FacebookService:
    """
    Service for Facebook Live streaming.
    
    Uses FacebookAuthService for authentication.
    """
    
    def __init__(self, auth_service: Optional[FacebookAuthService] = None):
        """
        Initialize FacebookService.
        
        Args:
            auth_service: Facebook authentication service
        """
        self.settings = get_settings()
        self.auth_service = auth_service or FacebookAuthService()
        self.logger = get_logger("ratteil.services.facebook")
    
    async def create_live_video(
        self,
        title: str,
        description: str,
        privacy: str = "EVERYONE"
    ) -> Dict[str, Any]:
        """
        Create a Facebook Live video.
        
        Args:
            title: Video title
            description: Video description
            privacy: Privacy setting
            
        Returns:
            Dictionary containing live video information
        """
        try:
            params = {
                'status': 'LIVE_NOW',
                'access_token': self.settings.facebook_access_token,
                'appsecret_proof': self.settings.facebook_app_secret,
                'title': title,
                'description': description,
                'privacy': f'{{"value": "{privacy}"}}'
            }
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://graph.facebook.com/v20.0/me/live_videos',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"Created live video: {data.get('id')}")
                        return data
                    else:
                        error_data = await response.json()
                        self.logger.error(f"Failed to create live video: {error_data}")
                        raise Exception(f"Failed to create live video: {error_data}")
                        
        except Exception as e:
            self.logger.error(f"Failed to create live video: {e}")
            raise
    
    async def end_live_video(self, video_id: str) -> bool:
        """
        End a Facebook Live video.
        
        Args:
            video_id: The live video ID
            
        Returns:
            True if successful
        """
        try:
            params = {
                'end_live_video': True,
                'access_token': self.settings.facebook_access_token,
                'appsecret_proof': self.settings.facebook_app_secret
            }
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://graph.facebook.com/v20.0/{video_id}",
                    params=params
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Ended live video: {video_id}")
                        return True
                    else:
                        error_data = await response.json()
                        self.logger.error(f"Failed to end live video: {error_data}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to end live video: {e}")
            return False
    
    async def get_stream_url(self, video_id: Optional[str] = None) -> str:
        """
        Get the RTMP stream URL for a live video.
        
        Args:
            video_id: Optional video ID (will create new if not provided)
            
        Returns:
            The RTMP stream URL
        """
        if video_id is None:
            # Create a new live video
            video = await self.create_live_video(
                title="RatTeil Stream",
                description="Quran recitation stream"
            )
            video_id = video.get('id')
        
        # Get stream URL from video info
        video_info = await self.get_live_video_info(video_id)
        stream_url = video_info.get('stream_url', '')
        
        # Clean up the URL (remove escape characters)
        cleaned_url = stream_url.replace('\\\\', '')
        return cleaned_url
    
    async def get_live_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get information about a live video.
        
        Args:
            video_id: The live video ID
            
        Returns:
            Dictionary containing video information
        """
        try:
            params = {
                'access_token': self.settings.facebook_access_token,
                'fields': 'id,title,description,stream_url,secure_stream_url,status'
            }
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://graph.facebook.com/v20.0/{video_id}",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.json()
                        self.logger.error(f"Failed to get video info: {error_data}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"Failed to get video info: {e}")
            return {}
