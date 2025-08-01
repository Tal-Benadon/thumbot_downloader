#!/usr/bin/env python3
"""
Test Instagram download with configuration system
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.cobalt_client import CobaltClient
from app.services.downloader import process_cobalt_download, download_video_from_url
from app.config import config
from app.exceptions import CobaltError, FileTooLargeError

def test_instagram_with_fallbacks():
    """Test Instagram download with fallback functionality"""
    url = "https://www.instagram.com/reel/DMM205mSJTy/?igsh=MTlxZ3J4czk3bDcxeg=="
    
    print(f"🎬 Testing Instagram download with fallbacks")
    print(f"URL: {url}")
    print("=" * 60)
    
    print(f"\n📋 Current Configuration:")
    print(f"  Video Quality: {config.cobalt.video_quality.value}")
    print(f"  Quality Fallbacks: {[q.value for q in config.cobalt.video_quality_fallbacks]}")
    print(f"  Video Codec: {config.cobalt.video_codec.value}")
    print(f"  Codec Fallbacks: {[c.value for c in config.cobalt.video_codec_fallbacks]}")
    print(f"  Audio Format: {config.cobalt.audio_format.value}")
    print(f"  Audio Fallbacks: {[a.value for a in config.cobalt.audio_format_fallbacks]}")
    print(f"  Max File Size: {config.cobalt.max_file_size_mb}MB ({config.cobalt.max_file_size} bytes)")
    print(f"  Picker Behavior: {config.cobalt.picker_behavior.value}")
    print(f"  Primary Instance: {config.cobalt.cobalt_instance_url}")
    print(f"  Fallback Instances: {len(config.cobalt.fallback_instances)} available")
    
    client = CobaltClient()
    
    try:
        # Get download info from Cobalt (will try settings fallbacks if needed)
        print(f"\n1. Getting video info from Cobalt with settings fallbacks...")
        response = client.download_video_with_fallbacks(url)
        print(f"✅ Cobalt response: {response}")
        
        # Process the response
        print(f"\n2. Processing Cobalt response...")
        processed = client.process_cobalt_response(response)
        print(f"✅ Processed response: {processed}")
        
        # Download the video file (but don't upload to Discord)
        if processed["type"] == "single":
            video_url = processed["url"]
            filename = processed.get("filename", "test_video.mp4")
            
            print(f"\n3. Downloading video file...")
            file_path = download_video_from_url(video_url, filename)
            
            # Check file info
            file_size = os.path.getsize(file_path)
            print(f"✅ Video downloaded successfully!")
            print(f"   File: {file_path}")
            print(f"   Size: {file_size / (1024*1024):.2f} MB")
            
            # Check if it's within our configured limits
            if file_size <= config.cobalt.max_file_size:
                print(f"✅ File size is within configured limit ({config.cobalt.max_file_size_mb}MB)")
            else:
                print(f"⚠️  File size exceeds configured limit ({config.cobalt.max_file_size_mb}MB)")
            
            return file_path
            
        elif processed["type"] == "picker":
            print(f"✅ Multiple files found, would use picker behavior: {config.cobalt.picker_behavior.value}")
            return "picker_response"
            
    except CobaltError as e:
        print(f"❌ Cobalt error: {e}")
        return None
    except FileTooLargeError as e:
        print(f"❌ File too large: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_different_configs():
    """Test with different configuration values"""
    print(f"\n🧪 Testing different configurations")
    print("=" * 40)
    
    # Test with different max file sizes
    test_sizes = [5.0, 25.0, 100.0]  # MB
    
    for size_mb in test_sizes:
        print(f"\n📏 Testing with max file size: {size_mb}MB")
        
        # Temporarily change config
        original_size = config.cobalt.max_file_size_mb
        config.cobalt.max_file_size_mb = size_mb
        config.cobalt.__post_init__()  # Trigger conversion
        
        print(f"   Configured limit: {config.cobalt.max_file_size} bytes")
        
        # Restore original
        config.cobalt.max_file_size_mb = original_size
        config.cobalt.__post_init__()

if __name__ == "__main__":
    print("🤖 ThumbBot Instagram Test with Configuration")
    print("=" * 50)
    
    # Test the Instagram download
    result = test_instagram_with_fallbacks()
    
    if result:
        print(f"\n🎉 Test completed successfully!")
        if result != "picker_response":
            print(f"   Downloaded file: {result}")
            
            # Clean up the test file
            try:
                if os.path.exists(result):
                    os.remove(result)
                    print(f"   Cleaned up test file")
            except Exception as e:
                print(f"   Warning: Could not clean up file: {e}")
    else:
        print(f"\n❌ Test failed")
    
    # Test configuration changes
    test_different_configs()