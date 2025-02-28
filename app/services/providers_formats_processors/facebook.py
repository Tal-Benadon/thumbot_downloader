from typing import Dict, Any
from app.exceptions import NoSupportedFormatAvailable

def choose_facebook_format(formats_info: Dict[str, Any]) -> str: #is listed per resolution for easier testing
    chosen_format = None
    
    # filter the formats dict to have no av01 vcodec (not widely supported)
    filtered_formats_info = {
        f: formats_info[f] for f in formats_info if 'av01' not in formats_info[f].get('vcodec')
    }
    
    # pprint.pprint(filtered_formats_info)
    # TODO: Add flag to flip priority to HD
    # we prioritize sd for less bandwith
    try:
        for priority in ["sd", "hd"]:                                
            if priority in filtered_formats_info:
                chosen_format = {
                    'format_id':priority, 
                    'format_url':filtered_formats_info[priority].get('format_url')
                }
                break # will break if sd is found
        
        
    # if sd nor hd are not found, try to salvage something with resolution without av01
    # TODO: could be adjusted to get a specific resolution
    # if not chosen_format:                         
    #     for format_id, format_values in filtered_formats_info.items():
    #         format_res = format_values.get('resolution')
    #         if format_res is not None and 'audio only' not in format_res:
    #             chosen_format = {
    #                 'format_id': format_id,
    #                 'format_url':format_values.get('format_url')
    #             }
    #             break
    
    # if still None
        if not chosen_format:
            raise NoSupportedFormatAvailable("avalible format not found")
    except NoSupportedFormatAvailable as e:
        return{"Error": {"FacebookError": e}}
        return chosen_format