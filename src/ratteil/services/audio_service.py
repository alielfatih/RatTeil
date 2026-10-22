import os
import subprocess
from pathlib import Path

def get_audio_length(file_path: str | Path) -> float:
    """Get audio file duration using ffprobe."""
    try:
        cmd = f'ffprobe -i {file_path} -show_entries format=duration -v quiet -of csv="p=0"'
        output = subprocess.check_output(cmd, shell=True).decode()
        file_length = float(output.strip()) / 60.0
        return float(str(file_length)[:6])
    except (subprocess.CalledProcessError, ValueError):
        if os.path.exists(file_path):
            os.remove(file_path)
        return 0.0

def merge_audios(audios: list[str], out_path: str | Path) -> None:
    """Merge multiple audio files using ffmpeg."""
    command = 'ffmpeg -loglevel error %s -filter_complex "%sconcat=n=%s:v=0:a=1" %s/fb_stream/merged.mp3'
    
    audio_cod = ""
    audio_inputs = ""
    n = len(audios)
    track_input = 0
    for audio in audios:
        audio_inputs += f" -i {audio}"
        audio_cod += f"[{track_input}:a]"
        track_input += 1
        
    merged_output_path = Path(out_path) / "fb_stream" / "merged.mp3"
    try:
        if merged_output_path.exists():
            os.remove(merged_output_path)
    except Exception:
        pass

    full_command = command % (audio_inputs, audio_cod, n, out_path)
    os.system(full_command)