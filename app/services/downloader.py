import yt_dlp
import requests
import os
import pprint
from app.exceptions import NoSupportedFormatAvailable, MissingContentLengthError, FileTooLargeError, InitialLinkFormatError
from typing import Any, Dict

video_dir = './video_temp_dir'

cookies_path = 'cookie.txt'




def extract_metadata_info(url: str) -> Dict[str, Any]:
    yt_opt = {
    'cookiefile': cookies_path
    }
    try:
        with yt_dlp.YoutubeDL(yt_opt) as ydl:
            video_info_dict = ydl.extract_info(url, download=False)
    
            return video_info_dict
        
    except Exception as e:
        print(f"Metadata extraction error found\n\n{e}") 





# Checks for the different formats and sizes existing in the given metadata
def metadata_formats_info(info_dict):
    formats_info = {}
    if 'formats' in info_dict:
        for format in info_dict['formats']:
            
            format_id = format.get('format_id')
            if not format_id:
                continue
            
            format_ext = format.get('ext', 'Unknown extension')
            format_note = format.get('format_note', 'Unknown note')
            format_url = format.get('url', None)
            vcodec = format.get('vcodec', '')
            filesize = format.get('filesize', None)
            filesize_approx = format.get('filesize_approx', None) 
            resolution = format.get('resolution', '')
            
            
            # size readablity
            if filesize is not None:
                filesize = round(int(filesize) / (1024 * 1024),2)
            if filesize_approx is not None:
                filesize_approx = round(int(filesize_approx) / (1024 * 1024),2)
                
            formats_info[format_id] = {
                'format_ext': format_ext,
                'format_note':format_note,
                'format_url':format_url,
                'vcodec': vcodec,
                'filesize': filesize,
                'filesize_approx':filesize_approx,
                'resolution': resolution
            }
    # pprint.pprint(formats_info)
    return formats_info



def choose_facebook_format(formats_info: Dict[str, Any]) -> str: #is listed per resolution for easier testing
    chosen_format = None
    
    # filter the formats dict to have no av01 vcodec (not widely supported)
    filtered_formats_info = {
        f: formats_info[f] for f in formats_info if 'av01' not in formats_info[f].get('vcodec')
    }
    
    # pprint.pprint(filtered_formats_info)
    # TODO: Add flag to flip priority to HD
    # we prioritize sd for less bandwith
    for priority in ["sd", "hd"]:                                
        if priority in filtered_formats_info:
            chosen_format = {
                'format_id':priority, 
                'format_url':filtered_formats_info[priority].get('format_url')
            }
            break # will break if sd is found
        
        
    # if sd nor hd are not found, try to salvage something with resolution without av01
    # TODO: could be adjusted to get a specific resolution
    if not chosen_format:                         
        for format_id, format_values in filtered_formats_info.items():
            format_res = format_values.get('resolution')
            if format_res is not None and 'audio only' not in format_res:
                chosen_format = {
                    'format_id': format_id,
                    'format_url':format_values.get('format_url')
                }
                break
    
    # if still None
    if not chosen_format:
        raise NoSupportedFormatAvailable("avalible format not found")
    # pprint.pprint(chosen_format)
    return chosen_format



def choose_instagram_format(formats_info: Dict[str, Any]) -> str:
    chosen_format = False
    list_360p  = []
    list_540p = []
    list_576p = []
    list_720p = []
    list_1080p = []
    audio_format = ''
    pprint.pprint(formats_info)
    filtered_formats = {
    f: formats_info[f] 
    for f in formats_info  
    if formats_info.get('vcodec') is None or 'av01' not in formats_info[f].get('vcodec')  
    }
    pprint.pprint(filtered_formats)
    for format_id, format_details in filtered_formats.items():
        resolution = format_details.get('resolution')
        format_video_url = format_details.get('format_url')
        vcodec = format_details.get('vcodec')
        if resolution == '360x640':
            list_360p.append({format_id : {'resolution': resolution, 'format_url': format_video_url, 'vcodec': vcodec}})
        if resolution == '540x960':
            list_540p.append({format_id : {'resolution': resolution, 'format_url': format_video_url, 'vcodec': vcodec}})
        if resolution == '576x1024':
            list_576p.append({format_id : {'resolution': resolution, 'format_url': format_video_url, 'vcodec': vcodec}})
        if resolution == '720x1280':
            list_720p.append({format_id : {'resolution': resolution, 'format_url': format_video_url, 'vcodec': vcodec}})
        if resolution == '1080x1920':
            list_1080p.append({format_id : {'resolution': resolution, 'format_url': format_video_url, 'vcodec': vcodec}})
        if resolution == 'audio only':
            audio_format = format_id
        # print(f"[{format_id}] [{resolution}] [{format_video_url}]")
        # print(f"{list_360p}\n\n{list_540p}\n\n{list_576p}\n\n{list_720p}\n\n{list_1080p}\n\n")
        
    
    
    # return chosen_format
    format_element = list_720p[4]  # get the first dictionary
    format_id = list(format_element.keys())[0]  # get the first key (ID)
    format_url = format_element[format_id].get("format_url") # access 'format_url'
    final_format_id =  f"{format_id + '+' + audio_format}"
    print(f"both formats {final_format_id}")
    return {'format_id': final_format_id, 'format_url' : format_url}
    # return list_720p[0][list(list_720p[0].keys())[0]]['format_url']
    return



def choose_reddit_format(formats_info: Dict[str, Any]) -> str:
    video_candidates = {}
    audio_candidates = {}
    for format_id, format_values in formats_info.items():
        vcodec = format_values.get('vcodec', '')
        resolution = format_values.get('resolution', '')
        format_url = format_values.get('format_url', '')  
        
        if 'av01' in vcodec or 'hls' in format_id or 'fallback' in format_id:
            continue
        
        if 'audio only' in resolution:
            if 'DASH_AUDIO_' in format_url:
                kbps = int(format_url.split('DASH_AUDIO_')[-1].split('.')[0])   
                audio_candidates[kbps] = format_id # creates a key value of kbps : format_id

        elif 'DASH_' in format_url:
            res = int(format_url.split('DASH_')[-1].split('.')[0])
            video_candidates[res] = format_id
            
    prefferd_resolution = [720, 480] # can be adjustable
    video_format_id = None
    sorted_res = sorted(video_candidates.keys(), reverse=True)
    
    for res in prefferd_resolution:
        if res in video_candidates:
            video_format_id = video_candidates[res]
            break
    
    if not video_format_id and sorted_res:
        video_format_id = video_candidates[sorted_res[0]]
            
   
    preffered_audio_kbps = [128, 64] # can be adjustable 
    audio_format_id = None
    sorted_kbps = sorted(audio_candidates.keys(), reverse=True) # creates a list of the keys, highest number first
    
    for kbps in preffered_audio_kbps: 
        if kbps in audio_candidates:
            audio_format_id = audio_candidates.get(kbps)
            break
        
    if not audio_format_id and sorted_kbps: # if there is not any of the preffered audio kbps bring the first high one
        audio_format_id = audio_candidates[sorted_kbps[0]]
    
    final_format_id = f'{video_format_id + '+' + audio_format_id}'

    return {'format_id': final_format_id,  'format_url': formats_info[video_format_id]['format_url']}


def choose_tiktok_format(formats_info: Dict[str, Any]) -> str:
    size_restriction = 15 # tiktok seems to provide filesize within the initial metadata
    video_candidates = {}
    # video_candidates2 = {}
    video_format = ''
    
    for format_id, format_values in formats_info.items():
        vcodec = format_values.get('vcodec', '')
        resolution = format_values.get('resolution', '')
        format_url = format_values.get('format_url', '')
        filesize = format_values.get('filesize', '')
        
        # video_candidates2[format_id] = {'vcodec': vcodec, 'resolution': resolution, 'format_url':format_url, 'filesize': filesize}
        if resolution:
            size = filesize
            video_candidates[size] = format_id # formats of same size are being overwritten, could be a fallback or location dependant provider
    sorted_by_size = sorted(video_candidates, reverse=True)
    print(sorted_by_size)
    for size in sorted_by_size:
        print(size)
        if size <= size_restriction:
            video_format = video_candidates[size]
            return {'format_id' : video_format, 'format_url': format_url}
    
                
    
    
        
def check_video_size(video_url: str, max_size=15_728_640)-> int:
    
    # Head request to determine actual video size
    response = requests.head(video_url, allow_redirects=True)
    content_length = response.headers.get('content-length')
    
    # Checks if size exists or exceeds the max size limits
    if not content_length:
        raise MissingContentLengthError("Content length not found in response headers.")
    
    content_length = int(content_length)
    
    if content_length >= max_size:
        raise FileTooLargeError(f"File size [{content_length} bytes] ({round(content_length / (1024 * 1024),2)}MB) exceeds the limit of [{max_size}] bytes ({max_size / (1024 * 1024)}MB)")
    
    return content_length
    




def download_video(url: str, format_id: str) -> str:
    video_path_template = os.path.join(video_dir,'%(title)s.%(ext)s')
    
    ydl_opts: Dict[str, Any] = {
         'format': format_id,
        'outtmpl': video_path_template,
        'cookiefile': cookies_path
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
            
    except Exception as e:
        print(f"Download Error{e}")
        
    return 
            

def choose_format(initial_link, format_info):
    
    dispatch_table = {
        'facebook': choose_facebook_format,
        'fb.watch': choose_facebook_format,
        'instagram': choose_instagram_format,
        'reddit': choose_reddit_format,
        'tiktok': choose_tiktok_format
    }
    
    for key, func in dispatch_table.items():
        if key in initial_link:
            if key == 'tiktok' and 'video' not in initial_link:
                continue
            return func(format_info)
        
    raise InitialLinkFormatError(f"Error: Unsupported link provider in URL [{initial_link}]")
                

def proccess_video_request(url: str):
    info_dict = extract_metadata_info(url)
    formats_info = metadata_formats_info(info_dict)
    chosen_format = choose_format(url, formats_info)
    video_size = check_video_size(chosen_format.get('format_url')) #from head request
    download_video(url, chosen_format.get('format_id'))
    
# def temp_main():
#     initial_link = "https://www.tiktok.com/@takamichihorror/video/7470145229941673234?is_from_webapp=1&sender_device=pc"
#     info_dict = extract_metadata_info(initial_link)
#     # print(info_dict)
#     formats_info = metadata_formats_info(info_dict)
            
#     chosen_format_url_dict = choose_format(initial_link, formats_info)
#     print(chosen_format_url_dict)
#     # video_url = info_dict.get('url')
#     video_size = check_video_size(chosen_format_url_dict.get('format_url'))
#     print(f" from head request: [{video_size}] ({round(video_size / (1024 * 1024), 2)}MB)")
#     download_video(initial_link, chosen_format_url_dict.get('format_id'))
#     return

# temp_main()

# *************** MOST OF THE AV01 WONT WORK FOR DISCORD, TRY RESORTING FOR SD OR HD ******************
#// ********** working size checks links list **************//#
# https://www.facebook.com/share/r/1X9i6Htg4r/ <- 9mb video, has av1 reduced to 500kb, has 720x has 1080x       
# https://www.instagram.com/reel/DFFcn61qQ1x/?igsh=MXN4c2txNTA5eHdzYQ== has 720x has 1080x 
# https://www.facebook.com/share/v/1A1tYB3oGk/ <- big video, has av1 that reduced it form 180 to 16 has 720x has 1080x 
# https://www.facebook.com/reel/1690243335234089 <- similar to the othe fb links
# https://www.facebook.com/share/v/14r6jGK6jgX/ <- has ONLY 480x854 res
# https://www.facebook.com/share/v/1ZMgYEge4q/ <- has ONLY 640x640 res
# https://www.reddit.com/r/EscapefromTarkov/comments/1iv9910/see_if_you_can_get_up_on_top_of_this_thing/
# https://www.reddit.com/r/marvelrivals/comments/1iugzk2/sneak_peak_of_the_new_magik_punkchild_skin/
# https://www.tiktok.com/@pygmalion_123/video/7466372263466585351?is_from_webapp=1&sender_device=pc