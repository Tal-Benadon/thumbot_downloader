#!/usr/bin/env python3
"""
Configuration management script for ThumbBot Downloader
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.config import config, VideoQuality, VideoCodec, AudioFormat, PickerBehavior

def show_current_config():
    """Display current configuration"""
    print("🔧 Current ThumbBot Configuration")
    print("=" * 50)
    
    print("\n📹 Video Settings:")
    print(f"  Quality: {config.cobalt.video_quality.value}")
    print(f"  Quality Fallbacks: {[q.value for q in config.cobalt.video_quality_fallbacks]}")
    print(f"  Codec: {config.cobalt.video_codec.value}")
    print(f"  Codec Fallbacks: {[c.value for c in config.cobalt.video_codec_fallbacks]}")
    print(f"  Audio Format: {config.cobalt.audio_format.value}")
    print(f"  Audio Fallbacks: {[a.value for a in config.cobalt.audio_format_fallbacks]}")
    print(f"  Audio Only: {config.cobalt.is_audio_only}")
    
    print("\n📁 File Handling:")
    print(f"  Max File Size: {config.cobalt.max_file_size / (1024*1024):.1f} MB")
    print(f"  Picker Behavior: {config.cobalt.picker_behavior.value}")
    print(f"  Strip Metadata: {config.cobalt.disable_metadata}")
    
    print("\n🌐 Cobalt Instance:")
    print(f"  Primary URL: {config.cobalt.cobalt_instance_url}")
    print(f"  Request Timeout: {config.cobalt.request_timeout}s")
    print(f"  Max Retries: {config.cobalt.max_retries}")
    
    print("\n💬 Discord Settings:")
    print(f"  Upload Limit: {config.discord.current_limit / (1024*1024):.1f} MB")
    print(f"  Upload Timeout: {config.discord.upload_timeout}s")
    
    print("\n🛠️ Platform Specific:")
    print(f"  TikTok H.265: {config.cobalt.tiktok_h265}")
    print(f"  Twitter GIF: {config.cobalt.twitter_gif}")
    print(f"  YouTube Dub Lang: {config.cobalt.youtube_dub_lang or 'None'}")
    
    print("\n📂 General:")
    print(f"  Debug Mode: {config.debug_mode}")
    print(f"  Log Level: {config.log_level}")
    print(f"  Temp Dir: {config.temp_dir}")
    print(f"  Auto Cleanup: {config.auto_cleanup}")

def show_available_options():
    """Show all available configuration options"""
    print("\n🎛️ Available Configuration Options")
    print("=" * 50)
    
    print("\n📹 Video Quality Options:")
    for quality in VideoQuality:
        print(f"  {quality.value} - {quality.name}")
    
    print("\n🎬 Video Codec Options:")
    for codec in VideoCodec:
        print(f"  {codec.value} - {codec.name}")
    
    print("\n🔊 Audio Format Options:")
    for audio in AudioFormat:
        print(f"  {audio.value} - {audio.name}")
    
    print("\n📂 Picker Behavior Options:")
    for behavior in PickerBehavior:
        print(f"  {behavior.value} - {behavior.name}")

def test_config():
    """Test current configuration with Cobalt"""
    print("\n🧪 Testing Configuration")
    print("=" * 30)
    
    try:
        from app.services.cobalt_client import CobaltClient
        
        client = CobaltClient()
        print(f"✅ Cobalt client created successfully")
        print(f"   Instance: {client.base_url}")
        
        # Test server connection
        try:
            server_info = client.get_server_info()
            print(f"✅ Server connection successful")
            print(f"   Version: {server_info.get('cobalt', {}).get('version', 'Unknown')}")
        except Exception as e:
            print(f"❌ Server connection failed: {e}")
        
        # Show what parameters would be sent
        params = config.cobalt.to_cobalt_params()
        print(f"\n📋 Cobalt API Parameters:")
        for key, value in params.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("🤖 ThumbBot Configuration Manager")
        print("=" * 40)
        print("\nUsage:")
        print("  python manage_config.py show     - Show current configuration")
        print("  python manage_config.py options  - Show available options")
        print("  python manage_config.py test     - Test current configuration")
        print("\nTo change settings, edit the environment variables or env.example file")
        return
    
    command = sys.argv[1].lower()
    
    if command == "show":
        show_current_config()
    elif command == "options":
        show_available_options()
    elif command == "test":
        test_config()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: show, options, test")

if __name__ == "__main__":
    main()