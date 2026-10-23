"""
YouTube service for RatTeil application.

Provides YouTube Live streaming functionality.
"""

from typing import Optional, Dict, Any
from pathlib import Path

from ratteil.config.settings import Settings, get_settings
from ratteil.auth.google_auth import YouTubeAuthService
from ratteil.utils.logging import get_logger


class YouTubeService:
    """
    Service for YouTube Live streaming.
    
    Uses YouTubeAuthService for authentication.
    """
    
    def __init__(self, auth_service: Optional[YouTubeAuthService] = None):
        """
        Initialize YouTubeService.
        
        Args:
            auth_service: YouTube authentication service
        """
        self.settings = get_settings()
        self.auth_service = auth_service or YouTubeAuthService()
        self.logger = get_logger("ratteil.services.youtube")
    
    async def create_live_broadcast(
        self,
        title: str,
        description: str,
        scheduled_start_time: Optional[str] = None,
        scheduled_end_time: Optional[str] = None,
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """
        Create a YouTube Live broadcast.
        
        Args:
            title: Broadcast title
            description: Broadcast description
            scheduled_start_time: Scheduled start time (ISO format)
            scheduled_end_time: Scheduled end time (ISO format)
            privacy_status: Broadcast privacy status
            
        Returns:
            Dictionary containing broadcast information
        """
        try:
            youtube = await self.auth_service.get_authenticated_client()
            
            broadcast_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "status": {
                    "privacyStatus": privacy_status,
                },
                "contentDetails": {
                    "enableAutoStart": True,
                    "enableAutoStop": True,
                }
            }
            
            if scheduled_start_time:
                broadcast_body["snippet"]["scheduledStartTime"] = scheduled_start_time
            if scheduled_end_time:
                broadcast_body["snippet"]["scheduledEndTime"] = scheduled_end_time
            
            request = youtube.liveBroadcasts().insert(
                part="snippet,status,contentDetails",
                body=broadcast_body
            )
            response = request.execute()
            
            self.logger.info(f"Created broadcast: {response['id']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create broadcast: {e}")
            raise
    
    async def create_live_stream(
        self,
        title: str,
        description: str,
        resolution: str = "1080p",
        frame_rate: str = "30fps"
    ) -> Dict[str, Any]:
        """
        Create a YouTube Live stream.
        
        Args:
            title: Stream title
            description: Stream description
            resolution: Stream resolution
            frame_rate: Stream frame rate
            
        Returns:
            Dictionary containing stream information
        """
        try:
            youtube = await self.auth_service.get_authenticated_client()
            
            stream_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "cdn": {
                    "resolution": resolution,
                    "frameRate": frame_rate,
                    "ingestionType": "rtmp",
                },
                "contentDetails": {
                    "isReusable": True,
                }
            }
            
            request = youtube.liveStreams().insert(
                part="snippet,cdn,contentDetails",
                body=stream_body
            )
            response = request.execute()
            
            # Save stream key
            stream_key = response["cdn"]["ingestionInfo"]["streamName"]
            stream_key_path = Path.home() / ".ratteil" / "stream_key.txt"
            stream_key_path.parent.mkdir(parents=True, exist_ok=True)
            stream_key_path.write_text(stream_key)
            
            self.logger.info(f"Created stream: {response['id']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create stream: {e}")
            raise
    
    async def bind_broadcast_to_stream(
        self,
        broadcast_id: str,
        stream_id: str
    ) -> Dict[str, Any]:
        """
        Bind a broadcast to a stream.
        
        Args:
            broadcast_id: The broadcast ID
            stream_id: The stream ID
            
        Returns:
            Dictionary containing binding information
        """
        try:
            youtube = await self.auth_service.get_authenticated_client()
            
            request = youtube.liveBroadcasts().bind(
                part="id,contentDetails",
                id=broadcast_id,
                streamId=stream_id
            )
            response = request.execute()
            
            self.logger.info(f"Bound broadcast {broadcast_id} to stream {stream_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to bind broadcast: {e}")
            raise
    
    async def get_stream_key(self) -> str:
        """
        Get the RTMP stream key.
        
        Returns:
            The stream key
        """
        stream_key_path = Path.home() / ".ratteil" / "stream_key.txt"
        if stream_key_path.exists():
            return stream_key_path.read_text().strip()
        
        # Create a new stream if no key exists
        stream = await self.create_live_stream(
            title="RatTeil Stream",
            description="Quran recitation stream"
        )
        return stream["cdn"]["ingestionInfo"]["streamName"]
    
    async def get_rtmp_url(self) -> str:
        """
        Get the RTMP URL for streaming.
        
        Returns:
            The RTMP URL
        """
        stream_key = await self.get_stream_key()
        return f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
