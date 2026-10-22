import os
import json
import random as r
import glob as g
import requests
from pathlib import Path
from ratteil.models.surah import SurahInfo
from ratteil.utils.file_utils import filename_resolve
from ratteil.services.audio_service import get_audio_length, merge_audios

class StreamService:
    def __init__(self, reciters_db: dict, resources_path: Path, ratteil_path: Path):
        self.reciters_db = reciters_db
        self.resources_path = resources_path
        self.ratteil_path = ratteil_path
        self.streams = []
        self.stream_title = ""
        self.stream_description = ""

    def prepare_stream_files(self, stream_files: list[str]) -> None:
        stream_length = 0.0
        max_stream_length = 75.0
        streams = []
        temp_stream = []
        
        files_queue = list(stream_files)
        while files_queue:
            addfile = files_queue[0]
            file_length = get_audio_length(addfile)
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

    def generate_stream_details(self, stream: list[str]) -> None:
        random_title = SurahInfo(*filename_resolve(r.choice(stream)), self.reciters_db).reciter.name
        self.stream_title = f"{random_title} || القرآن الكريم بث مباشر"
        stream_d = ""
        for surah in stream:
            info = SurahInfo(*filename_resolve(surah), self.reciters_db)
            stream_d += f"\n{info}"
        self.stream_description = stream_d

    def stream(self, stream: list[str], sites: list[str]) -> None:
        def stream_fixer(fixer: str, uri: str):
            os.system(f"ffmpeg -loglevel error -re -i {fixer} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 400k -bufsize 200k -shortest -strict experimental {uri}")

        fb_flag = False
        yt_flag = False
        yt_fb_flag = False
        
        if "youtube" in sites or "yt" in sites:
            yt_flag = True
            
        fbresponse = {}
        fburl = ""
        if "facebook" in sites or "fb" in sites:
            from ratteil.keys import RATTEIL_AC, RATTEIL_SE
            fb_flag = True
            params = {
                'status': 'LIVE_NOW',
                'access_token': RATTEIL_AC,
                'appsecret_proof': RATTEIL_SE,
                'title': self.stream_title,
                'description': self.stream_description,
                'privacy': json.dumps({'description': 'Everyone', 'value': 'EVERYONE'})
            }
            response = requests.post('https://graph.facebook.com/v20.0/me/live_videos', params=params)
            fbr = response.content.decode()
            fbresponse = eval(fbr)
            urly = fbresponse.get("secure_stream_url", "")
            for i in str(urly):
                if i != "\\":
                    fburl += i

        if yt_flag:
            os.system(f"python3 {self.ratteil_path}/create_stream.py -rPath {self.ratteil_path} --title '{self.stream_title}' --noauth_local_webserver --description '''{self.stream_description}''' -resPath {self.resources_path}")

        yt_url = None
        if len(sites) > 1:
            yt_fb_flag = True
            stream_key_path = self.resources_path / "stream_key.txt"
            youtube_stream_key = stream_key_path.read_text().strip()
            facebook_stream_url = fburl
            yt_url = f"-f flv rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}"
            uri = f"-flags:v +global_header -f tee -map 0:v -map 1:a '[f=flv]rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}|[f=flv]{facebook_stream_url}'"
        else:
            uri = "-f flv '''%s'''"
            if sites[0] in ["facebook", "fb"]:
                uri = uri % fburl
            else:
                stream_key_path = self.resources_path / "stream_key.txt"
                youtube_stream_key = stream_key_path.read_text().strip()
                uri = uri % f"rtmp://a.rtmp.youtube.com/live2/{youtube_stream_key}"

        starting_file = str(self.resources_path / "fixer" / "introduction.mp4")
        ending_file = str(self.resources_path / "fixer" / "conclusion.mp4")
        
        if not fb_flag:
            stream_fixer(starting_file, uri)
            for file in stream:
                img_list = g.glob(str(self.resources_path / "imgs/*"))
                chosen_img = r.choice(img_list) if img_list else ""
                os.system(f"ffmpeg -loglevel error -re -loop 1 -f image2 -i {chosen_img} -i {file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 800k -bufsize 400k -shortest -strict experimental {uri}")
            stream_fixer(ending_file, uri)
        else:
            merge_audios(stream, self.resources_path)
            if yt_fb_flag:
                stream_fixer(starting_file, yt_url)
            img_list = g.glob(str(self.resources_path / "imgs/*"))
            chosen_img = r.choice(img_list) if img_list else ""
            stream_file = str(self.resources_path / "fb_stream" / "merged.mp3")
            os.system(f"ffmpeg -loglevel error -re -loop 1 -f image2 -i {chosen_img} -i {stream_file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 800k -bufsize 400k -shortest -strict experimental {uri}")
            if yt_fb_flag:
                stream_fixer(ending_file, yt_url)

        if fb_flag:
            end_params = {
                'end_live_video': True,
                'access_token': RATTEIL_AC,
                'appsecret_proof': RATTEIL_SE
            }
            requests.post(f"https://graph.facebook.com/v20.0/{fbresponse.get('id')}", params=end_params)
            merged_path = self.resources_path / "fb_stream" / "merged.mp3"
            if merged_path.exists():
                os.remove(merged_path)