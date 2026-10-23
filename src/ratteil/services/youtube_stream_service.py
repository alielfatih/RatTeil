"""
YouTube stream creation service for RatTeil application.

This replaces the old create_stream.py with a modern, async implementation
using the new authentication system.
"""

import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from ratteil.config.settings import Settings, get_settings
from ratteil.auth.youtube_auth import YouTubeAuthService
from ratteil.config.exceptions import StreamError, AuthError
from ratteil.utils.logging import get_logger


class YouTubeStreamService:
    """
    Service for creating YouTube Live streams.
    
    Uses OAuth 2.0 device flow for non-GUI authentication.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize YouTubeStreamService.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or get_settings()
        self.auth_service = YouTubeAuthService(self.settings)
        self.logger = get_logger("ratteil.services.youtube_stream")

    async def create_stream(
        self,
        title: str,
        description: str,
        resources_path: Path,
        ratteil_path: Path,
        scheduled_start_time: Optional[str] = None,
        scheduled_end_time: Optional[str] = None,
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """
        Create a YouTube Live stream with broadcast.
        
        This is the main method that creates both the stream and the broadcast,
        and binds them together.
        
        Args:
            title: Stream title
            description: Stream description
            resources_path: Resources directory path
            ratteil_path: RatTeil package path
            scheduled_start_time: Optional scheduled start time (ISO format)
            scheduled_end_time: Optional scheduled end time (ISO format)
            privacy_status: Broadcast privacy status
            
        Returns:
            Dictionary containing stream and broadcast information
        """
        try:
            youtube = await self.auth_service.get_authenticated_client()
            
            # Create broadcast
            broadcast_response = await self._create_broadcast(
                youtube,
                title,
                description,
                scheduled_start_time,
                scheduled_end_time,
                privacy_status
            )
            broadcast_id = broadcast_response["id"]
            
            # Create stream
            stream_response = await self._create_stream(youtube, title, description)
            stream_id = stream_response["id"]
            
            # Bind broadcast to stream
            bind_response = await self._bind_broadcast(
                youtube,
                broadcast_id,
                stream_id
            )
            
            # Save stream key
            stream_key = stream_response["cdn"]["ingestionInfo"]["streamName"]
            stream_key_path = resources_path / "stream_key.txt"
            stream_key_path.write_text(stream_key)
            
            self.logger.info(
                f"Created YouTube stream: broadcast={broadcast_id}, "
                f"stream={stream_id}, key={stream_key}"
            )
            
            return {
                "broadcast": broadcast_response,
                "stream": stream_response,
                "bind": bind_response,
                "stream_key": stream_key,
                "rtmp_url": f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create YouTube stream: {e}")
            raise StreamError(
                f"Failed to create YouTube stream: {e}",
                platform="youtube"
            )
    
    async def _create_broadcast(
        self,
        youtube: Any,
        title: str,
        description: str,
        scheduled_start_time: Optional[str],
        scheduled_end_time: Optional[str],
        privacy_status: str
    ) -> Dict[str, Any]:
        """
        Create a YouTube Live broadcast.
        
        Args:
            youtube: Authenticated YouTube client
            title: Broadcast title
            description: Broadcast description
            scheduled_start_time: Scheduled start time (ISO format)
            scheduled_end_time: Scheduled end time (ISO format)
            privacy_status: Privacy status
            
        Returns:
            Broadcast response from YouTube API
        """
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
    
    async def _create_stream(
        self,
        youtube: Any,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Create a YouTube Live stream.
        
        Args:
            youtube: Authenticated YouTube client
            title: Stream title
            description: Stream description
            
        Returns:
            Stream response from YouTube API
        """
        stream_body = {
            "snippet": {
                "title": title,
                "description": description,
            },
            "cdn": {
                "resolution": "1080p",
                "frameRate": "30fps",
                "ingestionType": "rtmp",
            },
            "contentDetails": {
                "isReusable": True,
                "enableAutoStart": True,
                "enableAutoStop": True,
            }
        }
        
        request = youtube.liveStreams().insert(
            part="snippet,cdn,contentDetails",
            body=stream_body
        )
        response = request.execute()
        
        self.logger.info(f"Created stream: {response['id']}")
        return response
    
    async def _bind_broadcast(
        self,
        youtube: Any,
        broadcast_id: str,
        stream_id: str
    ) -> Dict[str, Any]:
        """
        Bind a broadcast to a stream.
        
        Args:
            youtube: Authenticated YouTube client
            broadcast_id: The broadcast ID
            stream_id: The stream ID
            
        Returns:
            Bind response from YouTube API
        """
        request = youtube.liveBroadcasts().bind(
            part="id,contentDetails",
            id=broadcast_id,
            streamId=stream_id
        )
        response = request.execute()
        
        self.logger.info(f"Bound broadcast {broadcast_id} to stream {stream_id}")
        return response


async def create_youtube_stream(
    title: str,
    description: str,
    resources_path: Path,
    ratteil_path: Path,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    privacy_status: str = "public"
) -> Dict[str, Any]:
    """
    Convenience function to create a YouTube stream.
    
    This is a standalone async function that can be called directly.
    
    Args:
        title: Stream title
        description: Stream description
        resources_path: Resources directory path
        ratteil_path: RatTeil package path
        start_time: Scheduled start time (ISO format)
        end_time: Scheduled end time (ISO format)
        privacy_status: Broadcast privacy status
        
    Returns:
        Dictionary containing stream information
    """
    service = YouTubeStreamService()
    return await service.create_stream(
        title,
        description,
        resources_path,
        ratteil_path,
        start_time,
        end_time,
        privacy_status
    )
