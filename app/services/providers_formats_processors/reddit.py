from typing import Dict, Any
from app.exceptions import NoSupportedFormatAvailable

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
    try:
        for kbps in preffered_audio_kbps: 
            if kbps in audio_candidates:
                audio_format_id = audio_candidates.get(kbps)
                break
            
        if not audio_format_id and sorted_kbps: # if there is not any of the preffered audio kbps bring the first high one
            audio_format_id = audio_candidates[sorted_kbps[0]]
        
        final_format_id = f"{video_format_id}+{audio_format_id}"
        if video_format_id is None or audio_format_id is None:
            raise NoSupportedFormatAvailable("Video or audio format not found in Reddit.py")
    except NoSupportedFormatAvailable as e:
        return {"Error": {"RedditError": e}}
    return {'format_id': final_format_id,  'format_url': formats_info[video_format_id]['format_url']}
