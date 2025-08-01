import requests
import os
from typing import Dict, Any, Optional, List
from app.exceptions import FileTooLargeError, InitialLinkFormatError, CobaltError
from app.config import config
import logging

logger = logging.getLogger(__name__)

class CobaltClient:
    """Client for interacting with Cobalt API instances"""
    
    def __init__(self, base_url: Optional[str] = None):
        # Use configured instance URL or provided URL
        self.base_url = base_url or config.cobalt.cobalt_instance_url
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'ThumbBot-Downloader/1.0'
        })
        
        # Set timeouts from config
        self.session.timeout = config.cobalt.request_timeout
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information from Cobalt instance"""
        try:
            response = self.session.get(f"{self.base_url}api/serverInfo")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get server info from {self.base_url}: {e}")
            raise CobaltError(f"Failed to connect to Cobalt instance: {e}")
    
    def download_video_with_fallbacks(self, url: str) -> Dict[str, Any]:
        """
        Download video with automatic fallbacks for quality, codec, and format
        
        Args:
            url: Video URL to download
        
        Returns:
            Dict containing the response from Cobalt API
        """
        # Get fallback lists from config
        qualities = config.cobalt.get_quality_fallback_list()
        codecs = config.cobalt.get_codec_fallback_list()
        audio_formats = config.cobalt.get_audio_fallback_list()
        
        logger.info(f"Trying download with fallbacks: qualities={qualities}, codecs={codecs}, audio={audio_formats}")
        
        # Try different combinations, starting with preferred settings
        for quality in qualities:
            for codec in codecs:
                for audio_format in audio_formats:
                    try:
                        logger.info(f"Attempting: quality={quality}, codec={codec}, audio={audio_format}")
                        
                        # Override config with current attempt
                        options = {
                            "vQuality": quality,
                            "vCodec": codec,
                            "aFormat": audio_format,
                            "filenamePattern": "basic",
                            "isAudioOnly": config.cobalt.is_audio_only,
                            "disableMetadata": config.cobalt.disable_metadata,
                        }
                        
                        # Add platform-specific settings
                        if config.cobalt.tiktok_h265:
                            options["tiktokH265"] = True
                        if config.cobalt.twitter_gif:
                            options["twitterGif"] = True
                        if config.cobalt.youtube_dub_lang:
                            options["youtubeDubLang"] = config.cobalt.youtube_dub_lang
                        
                        response = self.download_video(url, use_config=False, **options)
                        
                        # If we get here, the request succeeded
                        logger.info(f"✅ Success with: quality={quality}, codec={codec}, audio={audio_format}")
                        return response
                        
                    except CobaltError as e:
                        # If it's a settings-related error, try next combination
                        if "not available" in str(e).lower() or "unsupported" in str(e).lower():
                            logger.debug(f"Settings not available, trying next: {e}")
                            continue
                        else:
                            # If it's a different error, propagate it
                            logger.error(f"Non-fallback error: {e}")
                            raise
                    except Exception as e:
                        logger.debug(f"Error with quality={quality}, codec={codec}, audio={audio_format}: {e}")
                        continue
        
        # If we get here, all combinations failed
        raise CobaltError("All quality/codec/audio format combinations failed")

    def download_video(self, url: str, use_config: bool = True, **options) -> Dict[str, Any]:
        """
        Download video using Cobalt API
        
        Args:
            url: Video URL to download
            use_config: Whether to use configuration settings (default: True)
            **options: Additional options to override config settings
        
        Returns:
            Dict containing the response from Cobalt API
        """
        # For now, just use URL since extra parameters cause invalid_body error
        # TODO: Research correct parameter names for this Cobalt version
        payload = {
            "url": url
        }
        
        # Log what we would have sent with full config
        if use_config:
            full_params = config.cobalt.to_cobalt_params()
            logger.info(f"Would use config params: {full_params} (currently disabled due to API compatibility)")
        if options:
            logger.info(f"Would use options: {options} (currently disabled due to API compatibility)")
        
        # Try different endpoints that Cobalt instances might use
        endpoints = ["api/json", "", "api"]
        
        # Try primary instance first
        success = self._try_instance_endpoints(self.base_url, endpoints, payload)
        if success:
            return success
        
        # Try fallback instances
        logger.warning(f"Primary instance {self.base_url} failed, trying fallbacks...")
        for fallback_url in config.cobalt.fallback_instances:
            if not fallback_url.endswith('/'):
                fallback_url += '/'
            
            logger.info(f"Trying fallback instance: {fallback_url}")
            success = self._try_instance_endpoints(fallback_url, endpoints, payload)
            if success:
                logger.info(f"Successfully used fallback instance: {fallback_url}")
                return success
        
        # If we get here, all instances and endpoints failed
        raise CobaltError(f"All Cobalt instances failed. Tried: {self.base_url}, {', '.join(config.cobalt.fallback_instances)}")
    
    def _try_instance_endpoints(self, base_url: str, endpoints: List[str], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try different endpoints for a specific Cobalt instance"""
        for endpoint in endpoints:
            try:
                endpoint_url = f"{base_url}{endpoint}" if endpoint else base_url
                logger.debug(f"Trying endpoint: {endpoint_url}")
                
                response = self.session.post(endpoint_url, json=payload)
                
                # Skip 404 errors and try next endpoint
                if response.status_code == 404:
                    continue
                    
                response.raise_for_status()
                result = response.json()
                
                # Handle different response types
                if result.get("status") == "error":
                    error_code = result.get("error", {}).get("code", "unknown")
                    error_text = result.get("text", "Unknown error")
                    logger.error(f"Cobalt API error: {error_code} - {error_text}")
                    raise CobaltError(f"Cobalt error ({error_code}): {error_text}")
                
                logger.info(f"Successfully used endpoint: {endpoint_url}")
                return result
                
            except requests.RequestException as e:
                if "404" not in str(e):
                    logger.error(f"Failed to download video from {endpoint_url}: {e}")
                continue
        
        return None
    
    def process_cobalt_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Cobalt API response and extract download information
        
        Returns:
            Dict with processed download information
        """
        status = response.get("status")
        
        if status == "redirect" or status == "tunnel":
            # Single video file
            return {
                "type": "single",
                "url": response.get("url"),
                "filename": response.get("filename"),
                "status": status
            }
        
        elif status == "picker":
            # Multiple files (like Twitter threads)
            picker_items = response.get("picker", [])
            return {
                "type": "picker",
                "items": [
                    {
                        "url": item.get("url"),
                        "thumb": item.get("thumb")
                    }
                    for item in picker_items
                ],
                "status": status
            }
        
        elif status == "error":
            error_info = response.get("error", {})
            raise CobaltError(f"Cobalt processing error: {error_info}")
        
        else:
            logger.warning(f"Unknown Cobalt response status: {status}")
            return response

# Create a default client instance
default_client = CobaltClient()