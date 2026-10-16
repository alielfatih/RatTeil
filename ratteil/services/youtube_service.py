"""YouTube service for managing YouTube Live streaming."""

import datetime
from pathlib import Path
from typing import Optional, Tuple

from ratteil.config import get_settings, YouTubeError
from ratteil.models.stream import StreamDetails


class YouTubeService:
    """Service for YouTube Live API operations."""
    
    def __init__(self):
        """Initialize the YouTube service."""
        self.settings = get_settings()
        self._service = None
    
    def _get_authenticated_service(self):
        """Get authenticated YouTube service.
        
        This requires OAuth2 setup with client secrets.
        """
        if self._service is not None:
            return self._service
        
        try:
            from googleapiclient.discovery import build
            from oauth2client.client import flow_from_clientsecrets
            from oauth2client.file import Storage
            from oauth2client.tools import run_flow
        except ImportError as e:
            raise YouTubeError(
                "Google API client libraries not installed. "
                "Install with: pip install google-api-python-client oauth2client"
            ) from e
        
        # Get credentials
        client_secrets_file = self.settings.YOUTUBE_CLIENT_SECRETS
        credentials_file = self.settings.YOUTUBE_CREDENTIALS_FILE
        
        if not client_secrets_file:
            raise YouTubeError("YOUTUBE_CLIENT_SECRETS not configured")
        
        # Load credentials from file or run OAuth flow
        storage = Storage(credentials_file or 'credentials.json')
        credentials = storage.get()
        
        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(
                client_secrets_file,
                scope=[
                    "https://www.googleapis.com/auth/youtube",
                    "https://www.googleapis.com/auth/youtube.readonly",
                ],
                redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            )
            credentials = run_flow(flow, storage)
        
        # Build service
        self._service = build(
            'youtube',
            'v3',
            http=credentials.authorize(
                __import__('httplib2').Http()
            ),
        )
        
        return self._service
    
    def insert_stream(
        self,
        title: str,
        description: str,
        category_id: str = "28",  # Religion
    ) -> Tuple[str, str]:
        """Insert a new YouTube live stream.
        
        Args:
            title: Stream title
            description: Stream description
            category_id: YouTube category ID
            
        Returns:
            Tuple of (stream_id, broadcast_id)
        """
        try:
            youtube = self._get_authenticated_service()
            
            # Create liveStream resource
            stream_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "cdn": {
                    "format": "720p",
                    "ingestionType": "rtmp",
                },
            }
            
            stream_response = youtube.liveStreams().insert(
                part="snippet,cdn",
                body=stream_body,
            ).execute()
            
            stream_id = stream_response["id"]
            
            # Create liveBroadcast resource
            broadcast_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "scheduledStartTime": datetime.datetime.utcnow().isoformat() + "Z",
                    "scheduledEndTime": (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).isoformat() + "Z",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
                "contentDetails": {
                    "enableAutoStart": True,
                    "enableAutoStop": True,
                    "recordFromStart": True,
                    "enableDvr": True,
                    "enableEmbed": True,
                    "latencyPreference": "normal",
                    "enableClosedCaptions": False,
                },
            }
            
            broadcast_response = youtube.liveBroadcasts().insert(
                part="snippet,status,contentDetails",
                body=broadcast_body,
            ).execute()
            
            broadcast_id = broadcast_response["id"]
            
            # Bind stream to broadcast
            youtube.liveBroadcasts().bind(
                part="snippet",
                broadcastId=broadcast_id,
                streamId=stream_id,
            ).execute()
            
            return stream_id, broadcast_id
        except Exception as e:
            raise YouTubeError(f"Failed to create YouTube stream: {e}") from e
    
    def update_stream(
        self,
        broadcast_id: str,
        stream_details: StreamDetails,
    ) -> None:
        """Update a YouTube live stream with stream details.
        
        Args:
            broadcast_id: YouTube broadcast ID
            stream_details: Stream details to use for update
        """
        try:
            youtube = self._get_authenticated_service()
            
            broadcast_body = {
                "snippet": {
                    "title": stream_details.title,
                    "description": stream_details.description,
                },
            }
            
            youtube.liveBroadcasts().update(
                part="snippet",
                body=broadcast_body,
                broadcastId=broadcast_id,
            ).execute()
        except Exception as e:
            raise YouTubeError(f"Failed to update YouTube stream: {e}") from e
    
    def get_stream_url(
        self,
        stream_id: str,
    ) -> str:
        """Get the RTMP stream URL for a YouTube live stream.
        
        Args:
            stream_id: YouTube stream ID
            
        Returns:
            RTMP URL for streaming
        """
        try:
            youtube = self._get_authenticated_service()
            
            response = youtube.liveStreams().list(
                part="cdn",
                id=stream_id,
            ).execute()
            
            if response.get("items"):
                cdn = response["items"][0]["cdn"]
                return f"rtmp://{cdn['ingestionInfo']['ingestionAddress']}/{cdn['ingestionInfo']['streamName']}"
            
            raise YouTubeError("Stream not found")
        except Exception as e:
            raise YouTubeError(f"Failed to get stream URL: {e}") from e
    
    def start_stream(self, broadcast_id: str) -> None:
        """Start a YouTube live broadcast.
        
        Args:
            broadcast_id: YouTube broadcast ID
        """
        try:
            youtube = self._get_authenticated_service()
            
            youtube.liveBroadcasts().transition(
                part="status",
                broadcastId=broadcast_id,
                broadcastStatus="live",
            ).execute()
        except Exception as e:
            raise YouTubeError(f"Failed to start YouTube stream: {e}") from e
    
    def stop_stream(self, broadcast_id: str) -> None:
        """Stop a YouTube live broadcast.
        
        Args:
            broadcast_id: YouTube broadcast ID
        """
        try:
            youtube = self._get_authenticated_service()
            
            youtube.liveBroadcasts().transition(
                part="status",
                broadcastId=broadcast_id,
                broadcastStatus="complete",
            ).execute()
        except Exception as e:
            raise YouTubeError(f"Failed to stop YouTube stream: {e}") from e
    
    def create_and_start_stream(
        self,
        stream_details: StreamDetails,
    ) -> Tuple[str, str, str]:
        """Create and start a YouTube live stream.
        
        Args:
            stream_details: Stream details
            
        Returns:
            Tuple of (stream_id, broadcast_id, rtmp_url)
        """
        stream_id, broadcast_id = self.insert_stream(
            title=stream_details.title,
            description=stream_details.description,
        )
        
        # Store IDs in stream details
        stream_details.stream_id = stream_id
        stream_details.broadcast_id = broadcast_id
        
        # Get RTMP URL
        rtmp_url = self.get_stream_url(stream_id)
        stream_details.stream_url = rtmp_url
        
        # Start the stream
        self.start_stream(broadcast_id)
        stream_details.mark_live()
        
        return stream_id, broadcast_id, rtmp_url
