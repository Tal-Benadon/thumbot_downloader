#!/usr/bin/env python3
"""
Test Instagram video download with our Cobalt setup
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.cobalt_client import CobaltClient
from app.exceptions import CobaltError

def test_instagram_download():
    """Test downloading the Instagram reel"""
    url = "https://www.instagram.com/reel/DMM205mSJTy/?igsh=MTlxZ3J4czk3bDcxeg=="
    
    print(f"🎬 Testing Instagram download: {url}")
    print("=" * 60)
    
    client = CobaltClient()
    
    try:
        # Get download info from Cobalt
        print("\n1. Getting video info from Cobalt...")
        response = client.download_video(url)
        print(f"✅ Cobalt response: {response}")
        
        # Check if we got a direct download URL
        if response.get("status") == "redirect" and response.get("url"):
            download_url = response["url"]
            print(f"\n2. Download URL received: {download_url[:100]}...")
            
            # Download the actual file
            print("\n3. Downloading video file...")
            import requests
            
            video_response = requests.get(download_url, stream=True)
            video_response.raise_for_status()
            
            # Save to a file
            filename = response.get("filename", "instagram_video.mp4")
            filepath = f"./downloads/{filename}"
            
            # Create downloads directory if it doesn't exist
            os.makedirs("./downloads", exist_ok=True)
            
            with open(filepath, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Check file info
            file_size = os.path.getsize(filepath)
            print(f"✅ Video downloaded successfully!")
            print(f"   File: {filepath}")
            print(f"   Size: {file_size / (1024*1024):.2f} MB")
            
            return filepath
            
        else:
            print(f"❌ Unexpected response format: {response}")
            return None
            
    except CobaltError as e:
        print(f"❌ Cobalt error: {e}")
        return None
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

if __name__ == "__main__":
    filepath = test_instagram_download()
    
    if filepath:
        print(f"\n🎉 Success! Video saved to: {filepath}")
        print("\nFile details:")
        os.system(f"ls -lh '{filepath}'")
    else:
        print("\n❌ Download failed")