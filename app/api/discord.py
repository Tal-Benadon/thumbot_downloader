import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

def upload_to_discord( channel_id: str, file_path: str):
    uploadUrl = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    
    filename = os.path.basename(file_path)
    
    headers = {
        "Authorization" : f"Bot {DISCORD_TOKEN}"
    }
    
    payload_json = json.dumps({
            "content": "",
            "attachments": [{"id": 0, "filename": filename}]
        })
    
    
    with open(file_path, "rb") as file:
        files = {"files[0]": (filename, file)}
        try:
            response = requests.post(url=uploadUrl, headers=headers, data={"payload_json":payload_json}, files=files)
            response.raise_for_status()
            file.close()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload file: {e}")
            return None # for now
            
        
    
    
