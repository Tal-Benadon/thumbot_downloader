from typing import Dict, Any
from collections import defaultdict
from app.exceptions import NoSupportedFormatAvailable
def choose_instagram_format(formats_info: Dict[str, Any]) -> str:
    
    resolution_priority = ["720x1280", "1080x1920", "540x960", "576x1024","480x854","360x640"]
    
    categorized_formats = defaultdict(list)
    audio_format = None
   
    filtered_formats = {
    f: details
    for f, details in formats_info.items()  
    if details.get('vcodec') is None or 'av01' not in details.get('vcodec')  
    }
    
    for format_id, details in filtered_formats.items():
        resolution = details.get('resolution')
        if resolution == 'audio only' and audio_format == None:
            audio_format = format_id
        elif resolution in resolution_priority:
            categorized_formats[resolution].append({
                'format_id': format_id,
                'format_url': details.get('format_url'),
                'vcodec': details.get('vcodec')
            })
    try:
        for res in categorized_formats:
            if categorized_formats[res]:
                best_format = categorized_formats[res][-1]
                format_id = best_format["format_id"]
                format_url = best_format["format_url"]
                final_format_id = f"{format_id}+{audio_format}" 
                return {'format_id': final_format_id, 'format_url' : format_url}
            else:
                raise NoSupportedFormatAvailable("Error within instagram formatter, viable format not found")
            
    except NoSupportedFormatAvailable as e:
        return {"Error": {"InstagramError": e}}
        