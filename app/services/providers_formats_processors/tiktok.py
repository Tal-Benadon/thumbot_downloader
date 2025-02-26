from typing import Dict, Any

def choose_tiktok_format(formats_info: Dict[str, Any]) -> str:
    size_restriction = 15 # tiktok seems to provide filesize within the initial metadata
    video_candidates = {}
    video_format = ''
    
    for format_id, format_values in formats_info.items():
        vcodec = format_values.get('vcodec', '')
        resolution = format_values.get('resolution', '')
        format_url = format_values.get('format_url', '')
        filesize = format_values.get('filesize', '')
        
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