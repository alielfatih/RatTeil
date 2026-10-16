"""YouTube service for managing YouTube Live streaming.

Supports multiple authentication methods for headless environments:
- Service Account (JSON key file) - Recommended for servers
- OAuth2 Device Flow - For manual authentication
- API Key - Read-only operations only
"""

import datetime
import json
import sys
from pathlib import Path
from typing import Optional, Tuple, Literal

from ratteil.config import get_settings, YouTubeError
from ratteil.models.stream import StreamDetails


# Authentication mode type
AuthMode = Literal["service_account", "device_flow", "api_key"]


class YouTubeService:
    """Service for YouTube Live API operations.
    
    Supports headless authentication for servers without UI/browser.
    """
    
    def __init__(
        self,
        auth_mode: AuthMode = "device_flow",
        service_account_file: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the YouTube service.
        
        Args:
            auth_mode: Authentication mode to use
                - 'service_account': Use service account JSON key
                - 'device_flow': Use OAuth2 device flow (manual code entry)
                - 'api_key': Use API key (read-only)
            service_account_file: Path to service account JSON file
            api_key: YouTube API key for read-only operations
        """
        self.settings = get_settings()
        self.auth_mode = auth_mode
        self.service_account_file = service_account_file
        self.api_key = api_key or self.settings.YOUTUBE_API_KEY
        self._service = None
    
    def _get_authenticated_service(self):
        """Get authenticated YouTube service.
        
        Supports headless authentication without browser interaction.
        """
        if self._service is not None:
            return self._service
        
        try:
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError as e:
            raise YouTubeError(
                "Google API client libraries not installed. "
                "Install with: pip install google-api-python-client google-auth google-auth-oauthlib"
            ) from e
        
        if self.auth_mode == "service_account":
            return self._authenticate_service_account(build)
        elif self.auth_mode == "device_flow":
            return self._authenticate_device_flow(build)
        elif self.auth_mode == "api_key":
            return self._authenticate_api_key(build)
        else:
            raise YouTubeError(f"Unknown auth mode: {self.auth_mode}")
    
    def _authenticate_service_account(self, build):
        """Authenticate using service account JSON key."""
        from google.oauth2 import service_account
        
        if not self.service_account_file:
            service_account_file = self.settings.YOUTUBE_CLIENT_SECRETS
        else:
            service_account_file = self.service_account_file
        
        if not service_account_file:
            raise YouTubeError(
                "Service account file not configured. "
                "Set YOUTUBE_CLIENT_SECRETS or provide service_account_file."
            )
        
        if not Path(service_account_file).exists():
            raise YouTubeError(
                f"Service account file not found: {service_account_file}"
            )
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=[
                    "https://www.googleapis.com/auth/youtube",
                    "https://www.googleapis.com/auth/youtube.readonly",
                ],
            )
            
            self._service = build(
                'youtube',
                'v3',
                credentials=credentials,
            )
            return self._service
        except Exception as e:
            raise YouTubeError(f"Service account authentication failed: {e}") from e
    
    def _authenticate_device_flow(self, build):
        """Authenticate using OAuth2 device flow (headless).
        
        This prints a URL and code for the user to manually authenticate.
        """
        from google_auth_oauthlib.flow import InstalledAppFlow
        import httplib2
        
        client_secrets_file = self.settings.YOUTUBE_CLIENT_SECRETS
        credentials_file = self.settings.YOUTUBE_CREDENTIALS_FILE or 'youtube_credentials.json'
        
        if not client_secrets_file:
            raise YouTubeError(
                "OAuth2 client secrets file not configured. "
                "Set YOUTUBE_CLIENT_SECRETS."
            )
        
        if not Path(client_secrets_file).exists():
            raise YouTubeError(
                f"Client secrets file not found: {client_secrets_file}"
            )
        
        try:
            # Use device flow for headless authentication
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file,
                scopes=[
                    "https://www.googleapis.com/auth/youtube",
                    "https://www.googleapis.com/auth/youtube.readonly",
                ],
            )
            
            # For headless, we need to use the console flow
            # This will print a URL for the user to visit
            print("\n" + "="*60)
            print("YOUTUBE AUTHENTICATION REQUIRED")
            print("="*60)
            print("Please visit the following URL in a browser:")
            
            credentials = flow.run_console()
            
            self._service = build(
                'youtube',
                'v3',
                credentials=credentials,
            )
            return self._service
        except Exception as e:
            raise YouTubeError(f"OAuth2 authentication failed: {e}") from e
    
    def _authenticate_api_key(self, build):
        """Authenticate using API key (read-only)."""
        if not self.api_key:
            raise YouTubeError(
                "API key not configured. "
                "Set YOUTUBE_API_KEY or provide api_key."
            )
        
        try:
            self._service = build(
                'youtube',
                'v3',
                developerKey=self.api_key,
            )
            return self._service
        except Exception as e:
            raise YouTubeError(f"API key authentication failed: {e}") from e
    
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
    
    def get_available_auth_modes(self) -> list:
        """Get list of available authentication modes."""
        return ["service_account", "device_flow", "api_key"]
    
    def test_authentication(self) -> bool:
        """Test if authentication is working.
        
        Returns:
            True if authentication succeeds
        """
        try:
            service = self._get_authenticated_service()
            # Try a simple API call
            service.channels().list(part="id", mine=True).execute()
            return True
        except Exception as e:
            print(f"Authentication test failed: {e}")
            return False
