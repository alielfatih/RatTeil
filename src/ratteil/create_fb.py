import glob as g
def merge_audios(audios):
  command = 'ffmpeg %s -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1" output.mp'
  
  audio_inputs = ""
  n = len(audios)
  track_input = 0
  for audio in audios:
    audio_inputs = audio_inputs+"[%s:a]" % track_input
    track_input+=1
  
  print(command % audio_inputs)
  

merge_audios(g.glob("*.mp3"))