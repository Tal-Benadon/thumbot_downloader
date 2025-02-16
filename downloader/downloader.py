import yt_dlp
import requests
import os
import pprint
from typing import Any, Dict

video_dir = './video_temp_dir'


class MissingContentLengthError(Exception):
    """Raised when the Content-Length header is missing or invalid."""
    pass

class FileTooLargeError(Exception):
    """Raised when the file size exceeds the allowed limit."""
    pass



def extract_metadata_info(url: str) -> Dict[str, Any]:
    try:
        with yt_dlp.YoutubeDL() as ydl:
            video_info_dict = ydl.extract_info(url, download=False)
    
            return video_info_dict
        
    except Exception as e:
        print(f"downloader error found{e}") 



# Checks for the different formats and sizes existing in the given metadata
def metadata_format_info(info_dict):
    formats_info = []
    if 'formats' in info_dict:
        for format in info_dict['formats']:
            format_id = format.get('format_id')
            format_ext = format.get('ext', 'Unknown extension')
            format_note = format.get('format_note', 'Unknown note')
            filesize = format.get('filesize', None)
            filesize_approx = format.get('filesize_approx', None) 
            resulution = format.get('resolution', None)
            
            # size readablity
            if filesize is not None:
                filesize = round(int(filesize) / (1024 * 1024),2)
            if filesize_approx is not None:
                filesize_approx = round(int(filesize_approx) / (1024 * 1024),2)
                
            formats_info.append({
                'format_id': format_id,
                'format_ext': format_ext,
                'format_note':format_note,
                'filesize': filesize,
                'filesize_approx':filesize_approx,
                'resolution': resulution
            })
    pprint.pprint(formats_info)
    return formats_info

    
    
    
        
def check_video_size(video_url: str, max_size=15_728_640)-> int:
    
    # Head request to determine actual video size
    response = requests.head(video_url, allow_redirects=True)
    content_length = response.headers.get('content-length')
    
    # Checks if size exists or exceeds the max size limits
    if not content_length:
        raise MissingContentLengthError("Content length not found in response headers.")
    
    content_length = int(content_length)
    
    # if content_length >= max_size:
    #     raise FileTooLargeError(f"File size [{content_length} bytes] ({round(content_length / (1024 * 1024),2)}MB) exceeds the limit of [{max_size}] bytes ({max_size / (1024 * 1024)}MB)")
    
    return content_length
    




def download_video(url: str) -> str:
    video_path_template = os.path.join(video_dir,'%(title)s.%(ext)s')
    
    ydl_opts: Dict[str, Any] = {
         'format': "dash-1660324924885002vd",
        'outtmpl': video_path_template
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
            
    except Exception as e:
        print(f"Download Error{e}")
        
    return 
            
            


def temp_main():
    initial_link = "https://www.instagram.com/reel/DFFcn61qQ1x/?igsh=MXN4c2txNTA5eHdzYQ=="
    info_dict = extract_metadata_info(initial_link)
    # print(info_dict)
    metadata_format_info(info_dict)
    
    
    video_url = info_dict.get('url')
    video_size = check_video_size(video_url)
    print(f" from head request: [{video_size}] ({round(video_size / (1024 * 1024), 2)}MB)")
    download_video(initial_link)
    return

temp_main()


#// ********** working size checks links list **************//#
# https://www.facebook.com/share/r/1X9i6Htg4r/ <- 9mb video, has av1 reduced to 500kb          
# https://www.instagram.com/reel/DFFcn61qQ1x/?igsh=MXN4c2txNTA5eHdzYQ==
# https://www.facebook.com/share/v/1A1tYB3oGk/ <- big video, has av1 that reduced it form 180 to 16
# 
# 
# 
# 
# 
# 