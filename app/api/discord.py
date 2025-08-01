import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

def upload_to_discord(channel_id: str, file_path: str):
    """Upload a single file to Discord"""
    uploadUrl = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    
    filename = os.path.basename(file_path)
    
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}"
    }
    
    payload_json = json.dumps({
        "content": "",
        "attachments": [{"id": 0, "filename": filename}]
    })
    
    with open(file_path, "rb") as file:
        files = {"files[0]": (filename, file)}
        try:
            response = requests.post(url=uploadUrl, headers=headers, data={"payload_json": payload_json}, files=files)
            response.raise_for_status()
            return
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload file: {e}")
            return None


def upload_multiple_to_discord(channel_id: str, file_paths: list[str], content: str = ""):
    """Upload multiple files to Discord in a single message (max 10 files)"""
    uploadUrl = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    
    if not file_paths:
        return None
        
    # Discord allows max 10 attachments per message
    if len(file_paths) > 10:
        original_count = len(file_paths)
        file_paths = file_paths[:10]
        print(f"⚠️ Discord limit: Uploading 10/{original_count} files")
    
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}"
    }
    
    # Build attachments array for Discord API
    attachments = []
    files = {}
    
    for i, file_path in enumerate(file_paths):
        filename = os.path.basename(file_path)
        attachments.append({"id": i, "filename": filename})
        
        # Open file and add to files dict
        file_handle = open(file_path, "rb")
        files[f"files[{i}]"] = (filename, file_handle)
    
    payload_json = json.dumps({
        "content": content,
        "attachments": attachments
    })
    
    try:
        response = requests.post(
            url=uploadUrl, 
            headers=headers, 
            data={"payload_json": payload_json}, 
            files=files
        )
        response.raise_for_status()
        # Removed verbose success message
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to upload multiple files: {e}")
        return None
        
    finally:
        # Close all file handles
        for file_handle in files.values():
            if hasattr(file_handle[1], 'close'):
                file_handle[1].close()
