import requests
import os
import tempfile
import logging
from urllib.parse import urlparse
from app.exceptions import FileTooLargeError, CobaltError
from typing import Any, Dict, Optional
from .cobalt_client import default_client as cobalt_client
from app.config import config, PickerBehavior
# Import Discord functionality only when needed
try:
    from app.api.discord import upload_to_discord
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    def upload_to_discord(*args, **kwargs):
        raise ImportError("Discord functionality not available - missing dependencies") 

logger = logging.getLogger(__name__)

# Use configured temp directory
video_dir = config.temp_dir

# Ensure video directory exists
os.makedirs(video_dir, exist_ok=True)


def check_video_size(video_url: str, max_size: Optional[int] = None) -> int:
    """
    Check if video size is within Discord's limits
    
    Args:
        video_url: URL of the video to check
        max_size: Maximum allowed size in bytes (uses config if None)
    
    Returns:
        Size of the video in bytes
    
    Raises:
        FileTooLargeError: If the video is too large
    """
    if max_size is None:
        max_size = config.discord.current_limit
    try:
        response = requests.head(video_url, allow_redirects=True, timeout=10)
        response.raise_for_status()
        
        content_length = response.headers.get('content-length')
        if not content_length:
            # If we can't get the size, we'll have to try downloading and see
            logger.warning(f"Could not determine file size for {video_url}")
            return 0  # Return 0 to indicate unknown size
        
        content_length = int(content_length)
        
        if content_length >= max_size:
            size_mb = round(content_length / (1024 * 1024), 2)
            max_mb = max_size / (1024 * 1024)
            raise FileTooLargeError(
                f"File size [{content_length} bytes] ({size_mb}MB) exceeds the limit of [{max_size}] bytes ({max_mb}MB)"
            )
        
        return content_length
        
    except requests.RequestException as e:
        logger.warning(f"Could not check video size for {video_url}: {e}")
        return 0  # Return 0 to indicate unknown size


def download_video_from_url(video_url: str, filename: Optional[str] = None) -> str:
    """
    Download video from a direct URL
    
    Args:
        video_url: Direct URL to the video file
        filename: Optional filename, will be generated if not provided
    
    Returns:
        Path to the downloaded file
    """
    if not filename:
        # Generate filename from URL
        parsed_url = urlparse(video_url)
        filename = os.path.basename(parsed_url.path) or "video"
        
        # Ensure it has an extension
        if '.' not in filename:
            filename += '.mp4'
    
    # Ensure filename is safe
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
    file_path = os.path.join(video_dir, filename)
    
    try:
        logger.info(f"Downloading video from {video_url} to {file_path}")
        
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Check if we're getting a reasonable file size
        content_length = response.headers.get('content-length')
        if content_length:
            check_video_size(video_url)
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Successfully downloaded video to {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to download video from {video_url}: {e}")
        # Clean up partial file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        raise


def process_cobalt_download(cobalt_response: Dict[str, Any], channel_id: str = None) -> Optional[str]:
    """
    Process Cobalt API response and download the video
    
    Args:
        cobalt_response: Response from Cobalt API
        channel_id: Discord channel ID (needed for picker ALL behavior)
    
    Returns:
        Path to the downloaded file, or None if files were already processed and uploaded
    """
    processed = cobalt_client.process_cobalt_response(cobalt_response)
    
    if processed["type"] == "single":
        # Single video file
        video_url = processed["url"]
        filename = processed.get("filename")
        
        return download_video_from_url(video_url, filename)
    
    elif processed["type"] == "picker":
        # Multiple files - handle based on configuration
        items = processed["items"]
        if not items:
            raise CobaltError("No video files found in picker response")
        
        print(f"🔍 Picker: {len(items)} files found, behavior={config.cobalt.picker_behavior.value}")
        
        if config.cobalt.picker_behavior == PickerBehavior.FIRST:
            selected_item = items[0]
        elif config.cobalt.picker_behavior == PickerBehavior.LAST:
            selected_item = items[-1]

        elif config.cobalt.picker_behavior == PickerBehavior.ALL:
            print(f"📥 Downloading {len(items)} files...")
            downloaded_files = []
            
            for i, item in enumerate(items, 1):
                try:
                    # Extract original filename from URL
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(item["url"])
                    path = parsed_url.path
                    original_filename = os.path.basename(path)
                    
                    # Use original filename or create one with proper extension
                    if original_filename and '.' in original_filename:
                        filename = original_filename
                    else:
                        ext = os.path.splitext(path)[1] or '.bin'  # fallback to .bin if no extension
                        filename = f"media_{i}{ext}"
                    
                    file_path = download_video_from_url(item["url"], filename=filename)
                    downloaded_files.append(file_path)
                except Exception as e:
                    print(f"❌ Download failed for item {i}: {e}")
                    continue
            
            if downloaded_files:
                try:
                    from app.api.discord import upload_multiple_to_discord
                    upload_multiple_to_discord(channel_id, downloaded_files)
                    print(f"✅ Uploaded {len(downloaded_files)}/{len(items)} files")
                except Exception as e:
                    print(f"❌ Upload failed: {e}")
                
                # Clean up files
                if config.auto_cleanup:
                    for file_path in downloaded_files:
                        try:
                            if file_path and os.path.exists(file_path):
                                os.remove(file_path)
                        except Exception:
                            pass
            
            return None
        else:
            # Fallback: treat as ALL
            print(f"🔄 Unknown picker behavior, using ALL ({len(items)} files)")
            downloaded_files = []
            
            for i, item in enumerate(items, 1):
                try:
                    # Extract original filename from URL
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(item["url"])
                    path = parsed_url.path
                    original_filename = os.path.basename(path)
                    
                    # Use original filename or create one with proper extension
                    if original_filename and '.' in original_filename:
                        filename = original_filename
                    else:
                        ext = os.path.splitext(path)[1] or '.bin'  # fallback to .bin if no extension
                        filename = f"media_{i}{ext}"
                    
                    file_path = download_video_from_url(item["url"], filename=filename)
                    downloaded_files.append(file_path)
                except Exception as e:
                    print(f"❌ Fallback download failed for item {i}: {e}")
                    continue
            
            if downloaded_files:
                try:
                    from app.api.discord import upload_multiple_to_discord
                    upload_multiple_to_discord(channel_id, downloaded_files)
                    print(f"✅ Fallback uploaded {len(downloaded_files)}/{len(items)} files")
                except Exception as e:
                    print(f"❌ Fallback upload failed: {e}")
                
                if config.auto_cleanup:
                    for file_path in downloaded_files:
                        try:
                            if file_path and os.path.exists(file_path):
                                os.remove(file_path)
                        except Exception:
                            pass
            
            return None
    
    else:
        raise CobaltError(f"Unknown response type: {processed.get('type')}")
                
def proccess_video_request(url: str, channel_id: str):
    """
    Process a video download request using Cobalt API
    
    Args:
        url: Video URL to download
        channel_id: Discord channel ID to upload to
    """
    file_path = None
    
    try:
        logger.info(f"Processing video request for URL: {url}")
        
        # Get video information from Cobalt (with fallbacks)
        cobalt_response = cobalt_client.download_video_with_fallbacks(url)
        logger.info(f"Cobalt response status: {cobalt_response.get('status')}")
        
        # Download the video file
        file_path = process_cobalt_download(cobalt_response, channel_id)
        
        if file_path is None:
            # Files were already processed and uploaded (e.g., picker with ALL behavior)
            logger.info("Files already processed and uploaded")
        else:
            logger.info(f"Video downloaded to: {file_path}")
            
            # Upload to Discord (if available)
            if DISCORD_AVAILABLE:
                upload_result = upload_to_discord(channel_id, file_path)
                logger.info(f"Successfully uploaded to Discord: {upload_result}")
            else:
                logger.warning("Discord functionality not available - skipping upload")
        
        return {"success": True, "message": "Video processed and uploaded successfully"}
        
    except CobaltError as e:
        logger.error(f"Cobalt API error: {e}")
        return {"Error": f"Cobalt API Error -> {e}"}
    
    except FileTooLargeError as e:
        logger.error(f"File too large: {e}")
        return {"Error": f"File Too Large -> {e}"}
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"Error": f"Unexpected error occurred -> {e}"}
    
    finally:
        # Clean up downloaded file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {file_path}: {e}")