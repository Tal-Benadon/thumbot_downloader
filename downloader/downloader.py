import yt_dlp
import requests
import os
from typing import Any, Dict

video_dir = './video_temp_dir'


class ContentLengthError(Exception):
    pass

def get_file_size(url: str):
    response = requests.head(url, allow_redirects=True)
    content_length = response.headers.get('Content-Length')
    if content_length:
        print(content_length)
    else:
        print("failed content length")    
    return

# get_file_size("https://www.facebook.com/share/r/1X9i6Htg4r/")

def extract_info(url: str) -> Dict[str, Any]:
    try:
        with yt_dlp.YoutubeDL() as ydl:
            video_info_dict = ydl.extract_info(url, download=False)
            
            # Extract direct video url from metadata 
            video_url = video_info_dict.get('url')
            
            # Head request to determine actual video size
            response = requests.head(video_url, allow_redirects=True)
            content_length = response.headers.get('Content-length', 0)
            
            if content_length == 0:
                raise ContentLengthError("Content length not found")
            
            print(f"Content length = {int(content_length) / (1024 * 1024)}")
            return video_info_dict
        
    except ContentLengthError as e:
        print(f"downloader error found:\n{e}") 
    
info = extract_info("https://www.facebook.com/share/r/1X9i6Htg4r/")
# print(f"info {info}")


def download_video(url: str) -> str:
    video_path_template = os.path.join(video_dir,'%(title)s.%(ext)s')
    
    ydl_opts: Dict[str, Any] = {'outtmpl': video_path_template}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
            
    except:
        print("Download Error")
        
    return 
            
            
# download_video("https://www.facebook.com/share/r/1X9i6Htg4r/")
            