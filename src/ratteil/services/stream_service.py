"""
Stream service for RatTeil application.

Provides streaming functionality with async support.
"""

import os
import json
import random as r
import glob as g
import requests
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from ratteil.models.surah import SurahInfo
from ratteil.models.stream import StreamConfig, StreamDetails
from ratteil.config.settings import Settings, get_settings
from ratteil.config.exceptions import StreamError, FileError
from ratteil.services.audio_service import AudioService
from ratteil.auth.google_auth import YouTubeAuthService
from ratteil.auth.facebook_auth import FacebookAuthService
from ratteil.utils.file_utils import filename_resolve
from ratteil.utils.logging import get_logger


class StreamService:
    """
    Service for managing and executing streams.
    
    Provides both synchronous and asynchronous streaming operations.
    """
    
    def __init__(
        self,
        reciters_db: dict,
        resources_path: Path,
        ratteil_path: Path,
        settings: Optional[Settings] = None
    ):
        """
        Initialize StreamService.
        
        Args:
            reciters_db: Reciters database
            resources_path: Base resources directory
            ratteil_path: RatTeil package path
            settings: Application settings
        """
        self.reciters_db = reciters_db
        self.resources_path = Path(resources_path)
        self.ratteil_path = Path(ratteil_path)
        self.settings = settings or get_settings()
        self.audio_service = AudioService(self.settings)
        self.streams: List[List[str]] = []
        self.stream_title: str = ""
        self.stream_description: str = ""
        self.logger = get_logger("ratteil.services.stream")
        
        # Auth services
        self.youtube_auth = YouTubeAuthService(self.settings)
        self.facebook_auth = FacebookAuthService(self.settings)

    def prepare_stream_files(self, stream_files: List[str]) -> None:
        """
        Prepare stream files by grouping them into valid stream segments.
        
        Args:
            stream_files: List of audio file paths
        """
        stream_length = 0.0
        max_stream_length = self.settings.max_stream_length
        streams = []
        temp_stream = []
        
        files_queue = list(stream_files)
        while files_queue:
            addfile = files_queue[0]
            file_length = self.audio_service.get_audio_length(addfile)
            if file_length <= max_stream_length:
                if stream_length + file_length <= max_stream_length:
                    stream_length += file_length
                    if file_length > 0.0:
                        temp_stream.append(addfile)
                    files_queue.pop(0)
                else:
                    streams.append(temp_stream)
                    stream_length = 0.0
                    temp_stream = []
            else:
                log_file = self.resources_path / "logs.txt"
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"Audio file duration greater than {max_stream_length}m causes copyright issues; {addfile} = {file_length}m.\n")
                if os.path.exists(addfile):
                    os.remove(addfile)
                files_queue.pop(0)
        streams.append(temp_stream)
        self.streams = streams

    async def prepare_stream_files_async(self, stream_files: List[str]) -> None:
        """
        Prepare stream files asynchronously.
        
        Args:
            stream_files: List of audio file paths
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.prepare_stream_files, stream_files)

    def generate_stream_details(self, stream: List[str]) -> None:
        """
        Generate title and description for a stream.
        
        Args:
            stream: List of audio file paths
        """
        random_title = SurahInfo(*filename_resolve(r.choice(stream)), self.reciters_db).reciter.name
        self.stream_title = f"{random_title} || \u0627\u0644\u0642\u0631\u0622\u0646 \u0627\u0644\u0643\u0631\u064a\u0645 \u0628\u062b \u0645\u0628\u0627\u0634\u0631"
        stream_d = ""
        for surah in stream:
            info = SurahInfo(*filename_resolve(surah), self.reciters_db)
            stream_d += f"\n{info}"
        self.stream_description = stream_d

    async def generate_stream_details_async(self, stream: List[str]) -> None:
        """
        Generate stream details asynchronously.
        
        Args:
            stream: List of audio file paths
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.generate_stream_details, stream)

    async def create_youtube_stream(self, title: str, description: str) -> Dict[str, Any]:
        """
        Create a YouTube Live stream.
        
        Args:
            title: Stream title
            description: Stream description
            
        Returns:
            Dictionary containing stream information
        """
        try:
            youtube = await self.youtube_auth.get_authenticated_client()
            
            # Create stream
            stream_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "cdn": {
                    "resolution": self.settings.ffmpeg_path or "1080p",
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
            
            # Save stream key
            stream_key = response["cdn"]["ingestionInfo"]["streamName"]
            stream_key_path = self.resources_path / "stream_key.txt"
            stream_key_path.write_text(stream_key)
            
            self.logger.info(f"Created YouTube stream: {response['id']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create YouTube stream: {e}")
            raise StreamError(
                f"Failed to create YouTube stream: {e}",
                platform="youtube"
            )

    async def create_facebook_stream(self, title: str, description: str) -> Dict[str, Any]:
        """
        Create a Facebook Live stream.
        
        Args:
            title: Stream title
            description: Stream description
            
        Returns:
            Dictionary containing stream information
        """
        try:
            params = {
                'status': 'LIVE_NOW',
                'access_token': self.settings.facebook_access_token,
                'appsecret_proof': self.settings.facebook_app_secret,
                'title': title,
                'description': description,
                'privacy': json.dumps({'description': 'Everyone', 'value': 'EVERYONE'})
            }
            
            response = requests.post(
                'https://graph.facebook.com/v20.0/me/live_videos',
                params=params
            )
            fbr = response.json()
            
            self.logger.info(f"Created Facebook stream: {fbr.get('id')}")
            return fbr
            
        except Exception as e:
            self.logger.error(f"Failed to create Facebook stream: {e}")
            raise StreamError(
                f"Failed to create Facebook stream: {e}",
                platform="facebook"
            )

    def stream(self, stream: List[str], sites: List[str]) -> None:
        """
        Stream audio files to specified platforms (synchronous).
        
        Args:
            stream: List of audio file paths
            sites: List of platforms to stream to
        """
        def stream_fixer(fixer: str, uri: str):
            os.system(f"ffmpeg -loglevel error -re -i {fixer} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 400k -bufsize 200k -shortest -strict experimental {uri}")

        fb_flag = "facebook" in sites or "fb" in sites
        yt_flag = "youtube" in sites or "yt" in sites
        yt_fb_flag = fb_flag and yt_flag
        
        fbresponse = {}
        fburl = ""
        
        if fb_flag:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                fbresponse = loop.run_until_complete(
                    self.create_facebook_stream(self.stream_title, self.stream_description)
                )
                loop.close()
                urly = fbresponse.get("secure_stream_url", "")
                fburl = urly.replace("\\", "")
            except Exception as e:
                self.logger.error(f"Failed to create Facebook stream: {e}")
                fb_flag = False

        if yt_flag:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self.create_youtube_stream(self.stream_title, self.stream_description)
                )
                loop.close()
            except Exception as e:
                self.logger.error(f"Failed to create YouTube stream: {e}")
                yt_flag = False

        yt_url = None
        if yt_fb_flag:
            stream_key_path = self.resources_path / "stream_key.txt"
            youtube_stream_key = stream_key_path.read_text().strip()
            facebook_stream_url = fburl
            yt_url = f"-f flv rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}"
            uri = f"-flags:v +global_header -f tee -map 0:v -map 1:a '[f=flv]rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}|[f=flv]{facebook_stream_url}'"
        else:
            uri = "-f flv '%s'"
            if fb_flag and not yt_flag:
                uri = uri % fburl
            elif yt_flag and not fb_flag:
                stream_key_path = self.resources_path / "stream_key.txt"
                youtube_stream_key = stream_key_path.read_text().strip()
                uri = uri % f"rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}"
            else:
                uri = ""

        starting_file = str(self.resources_path / "fixer" / "introduction.mp4")
        ending_file = str(self.resources_path / "fixer" / "conclusion.mp4")
        
        if not fb_flag and not yt_flag:
            self.logger.error("No valid streaming platforms configured")
            return
        
        if not fb_flag:
            if uri:
                stream_fixer(starting_file, uri)
            for file in stream:
                img_list = g.glob(str(self.resources_path / "imgs/*"))
                chosen_img = r.choice(img_list) if img_list else ""
                if chosen_img:
                    os.system(f"ffmpeg -loglevel error -re -loop 1 -f image2 -i {chosen_img} -i {file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 800k -bufsize 400k -shortest -strict experimental {uri}")
            if uri:
                stream_fixer(ending_file, uri)
        else:
            self.audio_service.merge_audios(stream, self.resources_path)
            if yt_fb_flag:
                stream_fixer(starting_file, yt_url)
            img_list = g.glob(str(self.resources_path / "imgs/*"))
            chosen_img = r.choice(img_list) if img_list else ""
            stream_file = str(self.resources_path / "fb_stream" / "merged.mp3")
            if chosen_img:
                os.system(f"ffmpeg -loglevel error -re -loop 1 -f image2 -i {chosen_img} -i {stream_file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 800k -bufsize 400k -shortest -strict experimental {uri}")
            if yt_fb_flag:
                stream_fixer(ending_file, yt_url)

        if fb_flag and fbresponse.get('id'):
            end_params = {
                'end_live_video': True,
                'access_token': self.settings.facebook_access_token,
                'appsecret_proof': self.settings.facebook_app_secret
            }
            requests.post(f"https://graph.facebook.com/v20.0/{fbresponse.get('id')}", params=end_params)
            merged_path = self.resources_path / "fb_stream" / "merged.mp3"
            if merged_path.exists():
                merged_path.unlink()

    async def stream_async(self, stream: List[str], sites: List[str]) -> None:
        """
        Stream audio files to specified platforms (asynchronous).
        
        Args:
            stream: List of audio file paths
            sites: List of platforms to stream to
        """
        fb_flag = "facebook" in sites or "fb" in sites
        yt_flag = "youtube" in sites or "yt" in sites
        yt_fb_flag = fb_flag and yt_flag
        
        fbresponse = {}
        fburl = ""
        
        if fb_flag:
            try:
                fbresponse = await self.create_facebook_stream(self.stream_title, self.stream_description)
                urly = fbresponse.get("secure_stream_url", "")
                fburl = urly.replace("\\", "")
            except Exception as e:
                self.logger.error(f"Failed to create Facebook stream: {e}")
                fb_flag = False

        if yt_flag:
            try:
                await self.create_youtube_stream(self.stream_title, self.stream_description)
            except Exception as e:
                self.logger.error(f"Failed to create YouTube stream: {e}")
                yt_flag = False

        # Build FFmpeg command
        yt_url = None
        if yt_fb_flag:
            stream_key_path = self.resources_path / "stream_key.txt"
            youtube_stream_key = stream_key_path.read_text().strip()
            facebook_stream_url = fburl
            yt_url = f"-f flv rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}"
            uri = f"-flags:v +global_header -f tee -map 0:v -map 1:a '[f=flv]rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}|[f=flv]{facebook_stream_url}'"
        else:
            uri = "-f flv '%s'"
            if fb_flag and not yt_flag:
                uri = uri % fburl
            elif yt_flag and not fb_flag:
                stream_key_path = self.resources_path / "stream_key.txt"
                youtube_stream_key = stream_key_path.read_text().strip()
                uri = uri % f"rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}"
            else:
                uri = ""

        if not fb_flag and not yt_flag:
            self.logger.error("No valid streaming platforms configured")
            return
        
        starting_file = str(self.resources_path / "fixer" / "introduction.mp4")
        ending_file = str(self.resources_path / "fixer" / "conclusion.mp4")
        
        # Run FFmpeg commands
        def run_ffmpeg(cmd: str):
            os.system(cmd)
        
        if not fb_flag:
            if uri:
                run_ffmpeg(f"ffmpeg -loglevel error -re -i {starting_file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 400k -bufsize 200k -shortest -strict experimental {uri}")
            for file in stream:
                img_list = g.glob(str(self.resources_path / "imgs/*"))
                chosen_img = r.choice(img_list) if img_list else ""
                if chosen_img:
                    run_ffmpeg(f"ffmpeg -loglevel error -re -loop 1 -f image2 -i {chosen_img} -i {file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 800k -bufsize 400k -shortest -strict experimental {uri}")
            if uri:
                run_ffmpeg(f"ffmpeg -loglevel error -re -i {ending_file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 400k -bufsize 200k -shortest -strict experimental {uri}")
        else:
            await self.audio_service.merge_audios_async(stream, self.resources_path)
            if yt_fb_flag:
                run_ffmpeg(f"ffmpeg -loglevel error -re -i {starting_file} {yt_url}")
            img_list = g.glob(str(self.resources_path / "imgs/*"))
            chosen_img = r.choice(img_list) if img_list else ""
            stream_file = str(self.resources_path / "fb_stream" / "merged.mp3")
            if chosen_img:
                run_ffmpeg(f"ffmpeg -loglevel error -re -loop 1 -f image2 -i {chosen_img} -i {stream_file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 800k -bufsize 400k -shortest -strict experimental {uri}")
            if yt_fb_flag:
                run_ffmpeg(f"ffmpeg -loglevel error -re -i {ending_file} {yt_url}")

        if fb_flag and fbresponse.get('id'):
            end_params = {
                'end_live_video': True,
                'access_token': self.settings.facebook_access_token,
                'appsecret_proof': self.settings.facebook_app_secret
            }
            requests.post(f"https://graph.facebook.com/v20.0/{fbresponse.get('id')}", params=end_params)
            merged_path = self.resources_path / "fb_stream" / "merged.mp3"
            if merged_path.exists():
                merged_path.unlink()
