import random as r, os, requests
import subprocess, glob as g
# ratteil imports 
from ratteil.surahs import surah_list as su_list
import ratteil.dl as dl 
 
def surah_index_to_filename(x):
  """
    Convert number to surah filename.
  
    input: int; ex 1; filename will be
    output: str; 001.mp3
  """
  x = int(x)
  if x >= 100 and x <= 114:
    return  f"{x}.mp3"
  elif x < 10 and x > 0:
    return f"00{x}.mp3"
  elif x >= 10 and x < 100:
    return f"0{x}.mp3"
  else: 
    return f"{x} isn't valid surah index."
    
def filename_resolve(filename):
  """
    Get reciter code, surah number, and moshaf type.
    
    get reciter code surah number and moshaf type from surah filename to use them when generating stream title and description.
  """
  filename = filename[6:-4].split("@@")
  return [filename[-1],filename[0].split("/")[-1] ,filename[1]]

class SurahInfo:
  """
    Get information about specific surah
  """
  def __init__(self, index,code,mtype, recitersDB):
    self.id = index
    self.name = su_list[f"surah_{index}"]["name"]
    self.reciter = Reciter(code, recitersDB)
    self.moshaf = self.reciter.get_moshaf_name_url(int(mtype))
    self.dl_name = f"{code}@@{mtype}@@{self.id}.mp3"
    self.url = self.reciter.get_moshaf_name_url(int(mtype), True)

  def __str__(self):
    return f" سورة {self.name} برواية {self.moshaf} بصوت القاريء {self.reciter.name}."

class Reciter:
  """
    General information about reciter
    
    reciters available moshafs
    input: str; reciter code 
  """
  def __init__(self, reciter_code, recitersDB):
    self.code = reciter_code
    self.name = recitersDB[self.code]["name"]
    self.moshafs = recitersDB[self.code]["moshaf"]
    self.have_multi_moshafs = len(self.moshafs) > 1
    
    self.select_moshaf = r.choice(self.moshafs)
    self.selected_moshaf_type=self.select_moshaf["moshaf_type"]
    self.selected_moshaf_surahs_list = self.select_moshaf["surah_list"].split(",")
    self.selected_moshaf_url = self.select_moshaf["server"]
  
  def get_moshaf_name_url(self,mtype,url=False):
    for x in self.moshafs:
      if x["moshaf_type"] == mtype:
        if not url:
          return (x["name"])
        else:
          return (x["server"])
  
#made change test
class RatTeil:
  def __init__(self, recitersDB, recitersCodesDB, resourcesPath, ratteilPath):
    self.reciters_list = []
    self.reciters_with_multi_moshafs =  []
    self.stream_surahs_list = []
    self.streams = []
    self.recitersDB = recitersDB
    self.recitersCodesDB = recitersCodesDB
    self.resourcesPath = resourcesPath
    self.ratteilPath = ratteilPath
    self.stream_title = ""
    self.stream_description = ""
    self.selected_surahs_list = []
    
  def get_available_reciters_list(self):
    for code in self.recitersCodesDB:
      reciter = Reciter(code, self.recitersDB)
      self.reciters_list.append(f"code: {reciter.code}\tname: {reciter.name}")
    return self.reciters_list
      
  def get_reciters_with_multi_moshafs(self):
    for code in self.recitersCodesDB:
      reciter = Reciter(code, self.recitersDB)
      if reciter.have_multi_moshafs:
        self.reciters_with_multi_moshafs.append(code)
    return self.reciters_with_multi_moshafs
  
  def generate_random_reciters_list(self, list_length, reciters_codes_list, one_reciter):
    temp_list = []
    
    if list_length > len(reciters_codes_list):
      if len(reciters_codes_list) < 10:
        list_length = r.randrange(1,len(reciters_codes_list))
      else:
        list_length = r.randrange(3,6)
        
    while len(temp_list) != list_length:
      reciter_code = r.choice(reciters_codes_list)
      if not one_reciter and reciter_code not in temp_list :
        temp_list.append(reciter_code)
      else:
        temp_list.append(reciter_code)
    self.reciters_list = temp_list
    
    for x in temp_list: # fix repeatedly choose the same surah for the reciter
      reciter = Reciter(x, self.recitersDB)
      y = []
      for i in reciter.selected_moshaf_surahs_list:
        s = SurahInfo(i,x,reciter.selected_moshaf_type, self.recitersDB)
        self.selected_surahs_list.append(f"audios/{s.dl_name}")
        
  # need development
  def generate_random_surahs_list(self,list_length, surah_index):
    
    temp_list = []
    SHRANK = False
    if not list_length <= len(self.selected_surahs_list):
      list_length = len(self.selected_surahs_list)
    while len(temp_list) != list_length:
      if not surah_index:
        x = r.choice(self.selected_surahs_list)
      else:
        shrank_list = [] 
        for i in self.selected_surahs_list:
          if f"{surah_index}.mp3" in i:
            shrank_list.append(i)
        if len(shrank_list)==0:
          break
        if not SHRANK:
          list_length = len(shrank_list)
        x = r.choice(shrank_list)
      self.selected_surahs_list.remove(x)
      temp_list.append(x)
    self.stream_surahs_list = temp_list
    
  def get_length(self,file):
    """
      Get audio file duration.
    """
    try:
      
      fileLength = (float(subprocess.check_output(f'ffprobe -i {file} -show_entries format=duration -v quiet -of csv="p=0"', shell=True)[:-2])/60)
      fileLength = float(str(fileLength)[:6])
      return fileLength
    except subprocess.CalledProcessError:
      os.remove(file)
      return 0.0
  
  def prepare_stream_files(self,streamFiles):
    """
      Split a large stream into small streams.
      
      split stream to a number of streams of max length equal max_stream_length
      #default 75 minute.
    """
    streamLength = 0.0
    max_stream_length = 75.0 # 1:15 
    streams = []
    temp_stream = []
    
    while len(streamFiles) != 0:
      addfile = streamFiles[0]
      fileLength = self.get_length(addfile)
      if fileLength <= max_stream_length:
        if streamLength + fileLength <= max_stream_length :
          streamLength += fileLength
          if fileLength > 0.0:
            temp_stream.append(addfile)
          streamFiles.remove(addfile)
        else:
          streams.append(temp_stream)
          streamLength = 0.0 
          temp_stream = []
      else:
        print(f"skipping... {addfile}, see logfile for details.") # to avoid copyright claims while streaming; when using cc content without been added to cc holder allowed list
        f = open(f"{self.resourcesPath}/logs.txt", "a")
        f.write(f"Audio file with duration greater than {max_stream_length}m, will cuases copyrights issues when using cc content; {addfile} = {fileLength}m.\n")
        f.close()
        streamFiles.remove(addfile)
    streams.append(temp_stream)
    self.streams = streams
  
  def generate_stream_details(self, stream):
    """
      Generate title and description for stream
    
    """
    streamD = ""
    random_title = SurahInfo(*filename_resolve(r.choice(stream)), self.recitersDB).reciter.name 
    self.stream_title = "%s || القرآن الكريم بث مباشر" % random_title
    for surah in stream:
      info = SurahInfo(*filename_resolve(surah), self.recitersDB)
      streamD += f"\n{info}"
    
    self.stream_description = f"""{streamD}"""
  
  def stream(self, stream, sites):
    """
      Luanch streaming process
      
      call youtube api to create stream and start streaming stream content
    """
    def streamFixer(fixer,URI): # avoid repetition when streaming intro and end
      """
        Stream intro and conclusion video.
      """
      os.system(f"ffmpeg -loglevel error -re -i {fixer} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 400k -bufsize 200k -shortest -strict experimental {URI}")
    
    fb_falg = False
    yt_falg = False
    
    if "youtube" in sites:
      yt_falg = True
    if "facebook" in sites:
      from ratteil.keys import RATTEIL_AC,RATTEIL_SE
      fb_falg = True
      
    # new  youtube stream event
    if yt_falg:
      os.system(f"python3 {self.ratteilPath}/create_stream.py -rPath {self.ratteilPath} --title '{self.stream_title}' --noauth_local_webserver --description '''{self.stream_description}''' -resPath {self.resourcesPath}")
    
    # start fb stream
    if fb_falg:
      params = {
      'status': 'LIVE_NOW',
      'access_token': RATTEIL_AC,
      'appsecret_proof': RATTEIL_SE,
      'title': self.stream_title,
      'description': self.stream_description,
      }
      response = requests.post('https://graph.facebook.com/v20.0/me/live_videos', params=params)
      fbr = response.content.decode()
      fbresponse = eval(fbr)
      urly = fbresponse["secure_stream_url"]
      fburl = ""
      urly = list(urly)
      for i in urly:
        if i != "\\":
          fburl = fburl+i

    
    
    # getStream key
    if len(sites) > 1:
      YOUTUBE_STREAM_KEY = open(f"{self.resourcesPath}/stream_key.txt").read().strip()
      FACEBOOk_STREAM_URL = fburl
      
      URI = f"-flags:v +global_header -f tee -map 0:v -map 1:a '[f=flv]rtmp://a.rtmp.youtube.com/live2/{YOUTUBE_STREAM_KEY}|[f=flv]{FACEBOOk_STREAM_URL}'"
      
    else:
      URI = "-f flv %s"
      if sites[0] == "facebook":
        URI = URI % fburl #fbresponse["secure_stream_url"]
      else:
        YOUTUBE_STREAM_KEY = open(f"{self.resourcesPath}/stream_key.txt").read()
        URI = URI % f"rtmp://a.rtmp.youtube.com/live2/{YOUTUBE_STREAM_KEY}"
    # to avoid you cutting seconds from stream
    startingFile = f"{self.resourcesPath}/fixer/introduction.mp4"
    endingFile = f"{self.resourcesPath}/fixer/conclusion.mp4"
    
    streamFixer(startingFile,URI) #stream intro
    for file in stream: #stream a stream content
      imglist = g.glob(f"{self.resourcesPath}/imgs/*") 
      os.system(f"ffmpeg -loglevel error -re -loop 1 -f image2 -i {r.choice(imglist)} -i {file} -c:v libx264 -pix_fmt yuv420p -preset veryfast -b:v 800k -r 30.0 -g 60.0 -c:a aac -b:a 128k -ac 2 -maxrate 800k -bufsize 400k -shortest -strict experimental {URI}")
      
    streamFixer(endingFile,URI) #stream ending
    if fb_falg:
      end_params = {
        'end_live_video': True,
        'access_token': os.environ['RATTEIL_AC'],
        'appsecret_proof': os.environ['RATTEIL_SE']
      }
      requests.post(f"https://graph.facebook.com/v20.0/{fbresponse['id']}", params=end_params)
      
    
def stream_validation(ratteil,max_len, streamFiles, minimum, reciters_code, prevoius_len):
  """
    Assure audio files duration up to the minimum
    
    Check if audio files duration meet minimum requirement and if not; start
    revalidation process by downloading more audios until minimum requirement
    get met. 
  """
  #minimum by default 450.0 minutes #7.5 hours
  duration = 0.0
  if prevoius_len:
    duration = prevoius_len
  else:
    for file in streamFiles:
      file_len = ratteil.get_length(file)
      if file_len > 0.0:
        duration += file_len
      else:
        streamFiles.remove(file)
  
  if minimum > max_len:
    minimum = max_len 
  while duration < minimum: # download more audio files if downloaded file duration not met the minimum duration of stream
    
    ratteil.generate_random_reciters_list(1,reciters_code,False)
    ratteil.generate_random_surahs_list(1, None)
    
    
    x = ratteil.stream_surahs_list[0]
    surah = SurahInfo(*filename_resolve(x), ratteil.recitersDB).dl_name # downloading name for surah
    
    new_len,max_st = dl.dl(ratteil, max_len, ratteil.stream_surahs_list, ratteil.recitersDB, ratteil.resourcesPath, True, duration) # download selected surah
    duration = new_len
    
  return duration
