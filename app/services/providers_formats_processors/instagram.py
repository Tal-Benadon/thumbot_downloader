from typing import Dict, Any
from collections import defaultdict
def choose_instagram_format(formats_info: Dict[str, Any]) -> str:
    
    
    list_360p  = []
    list_540p = []
    list_576p = []
    list_720p = []
    list_1080p = []
    audio_format = ''
    
    filtered_formats = {
    f: formats_info[f] 
    for f in formats_info  
    if formats_info.get('vcodec') is None or 'av01' not in formats_info[f].get('vcodec')  
    }
    
    for format_id, format_details in filtered_formats.items():
        resolution = format_details.get('resolution')
        format_video_url = format_details.get('format_url')
        vcodec = format_details.get('vcodec')
        format_dict_element = {
            format_id:{
            'resolution': resolution,
            'format_url': format_video_url,
            'vcodec': vcodec
            }
            
        }
        if resolution == '360x640':
            list_360p.append(format_dict_element)
        if resolution == '540x960':
            list_540p.append(format_dict_element)
        if resolution == '576x1024':
            list_576p.append(format_dict_element)
        if resolution == '720x1280':
            list_720p.append(format_dict_element)
        if resolution == '1080x1920':
            list_1080p.append(format_dict_element)
        if resolution == 'audio only':
            audio_format = format_id

    priority = [list_720p, list_1080p, list_540p, list_576p, list_360p]
    for format_list in priority:
        length = len(format_list)
        if length > 0:
            format_element = format_list[length-1]
    
    format_id = list(format_element.keys())[0]  # get the first key (ID)
    format_url = format_element[format_id].get("format_url") 
    final_format_id =  f"{format_id + '+' + audio_format}"
    return {'format_id': final_format_id, 'format_url' : format_url}