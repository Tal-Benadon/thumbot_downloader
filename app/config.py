"""
Configuration settings for ThumbBot Downloader with Cobalt
"""

import os
from typing import Optional, Literal, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class VideoQuality(Enum):
    """Video quality options for downloads"""
    MAX = "max"        # Highest available quality
    UHD_8K = "8k+"     # 8K+ (7680×4320+)
    UHD_4K = "4k"      # 4K (3840×2160)
    QHD = "1440p"      # 2K/QHD (2560×1440)
    FHD = "1080p"      # Full HD (1920×1080)
    HD = "720p"        # HD (1280×720)
    SD = "480p"        # SD (854×480)
    LOW = "360p"       # Low (640×360)
    MOBILE = "240p"    # Mobile (426×240)
    MIN = "144p"       # Minimum (256×144)

class VideoCodec(Enum):
    """Video codec preferences"""
    H264 = "h264"      # H.264 - Best compatibility, max 1080p
    AV1 = "av1"        # AV1 - Best quality/efficiency, supports 8K & HDR
    VP9 = "vp9"        # VP9 - Same quality as AV1, ~2x bigger files, supports 4K & HDR

class AudioFormat(Enum):
    """Audio format options"""
    BEST = "best"      # Best available audio (alias for MP3)
    MP3 = "mp3"        # MP3 format
    OGG = "ogg"        # OGG format
    WAV = "wav"        # WAV format
    OPUS = "opus"      # Opus format

class FileFormat(Enum):
    """Container format options"""
    MP4 = "mp4"        # MP4 container
    WEBM = "webm"      # WebM container
    MKV = "mkv"        # Matroska container

class PickerBehavior(Enum):
    """How to handle multiple files (picker responses)"""
    FIRST = "first"    # Download only the first file
    LAST = "last"      # Download only the last file
    ALL = "all"        # Download all files (zip them)

@dataclass
class CobaltConfig:
    """Configuration for Cobalt API requests"""
    
    # Video Quality Settings
    video_quality: VideoQuality = VideoQuality.FHD
    video_codec: VideoCodec = VideoCodec.H264
    audio_format: AudioFormat = AudioFormat.BEST
    file_format: FileFormat = FileFormat.MP4
    
    # Fallback Settings (when preferred options aren't available)
    video_quality_fallbacks: list[VideoQuality] = field(default_factory=lambda: [
        VideoQuality.HD,      # 720p
        VideoQuality.SD,      # 480p
        VideoQuality.LOW,     # 360p
        VideoQuality.MOBILE   # 240p
    ])
    
    video_codec_fallbacks: list[VideoCodec] = field(default_factory=lambda: [
        VideoCodec.H264,  # Most compatible
        VideoCodec.VP9,   # Good quality
        VideoCodec.AV1    # Best quality but least compatible
    ])
    
    audio_format_fallbacks: list[AudioFormat] = field(default_factory=lambda: [
        AudioFormat.MP3,   # Most compatible
        AudioFormat.OGG,   # Good quality
        AudioFormat.OPUS,  # Best quality
        AudioFormat.WAV    # Uncompressed
    ])
    
    # Audio-only downloads
    is_audio_only: bool = False
    
    # Multiple files handling
    picker_behavior: PickerBehavior = PickerBehavior.ALL
    
    # File size limits (in bytes)
    max_file_size: int = 8_388_608  # 8MB (Discord's free tier limit)
    max_file_size_premium: int = 104_857_600  # 100MB (Discord Nitro limit)
    
    # File size limits in MB (easier configuration)
    max_file_size_mb: float = 8.0  # 8MB (Discord's free tier limit)
    
    def __post_init__(self):
        """Convert MB to bytes if MB value is provided"""
        # If max_file_size_mb is different from default, use it to set max_file_size
        if self.max_file_size_mb != 8.0:
            self.max_file_size = int(self.max_file_size_mb * 1024 * 1024)
    
    # Filename settings
    disable_metadata: bool = False  # Strip metadata from files
    filename_pattern: Optional[str] = None  # Custom filename pattern
    
    # Platform-specific settings
    tiktok_h265: bool = False  # Allow H.265 for TikTok (better quality, worse compatibility)
    twitter_gif: bool = False  # Convert Twitter loops to GIF
    youtube_dub_lang: Optional[str] = None  # YouTube dubbed language (e.g., "en", "es")
    
    # Retry and timeout settings
    request_timeout: int = 30  # Seconds to wait for Cobalt API response
    download_timeout: int = 300  # Seconds to wait for file download
    max_retries: int = 3  # Maximum retry attempts
    
    # Instance settings
    cobalt_instance_url: str = "http://localhost:9000"
    fallback_instances: list[str] = field(default_factory=lambda: [
        # No fallback instances - use only our local Cobalt instance
    ])
    
    def to_cobalt_params(self) -> Dict[str, Any]:
        """Convert config to Cobalt API parameters"""
        params = {
            "vQuality": self.video_quality.value,
            "vCodec": self.video_codec.value,
            "aFormat": self.audio_format.value,
            "filenamePattern": "basic",  # Use basic filename pattern
            "isAudioOnly": self.is_audio_only,
            "disableMetadata": self.disable_metadata,
        }
        
        # Platform-specific settings
        if self.tiktok_h265:
            params["tiktokH265"] = True
        if self.twitter_gif:
            params["twitterGif"] = True
        if self.youtube_dub_lang:
            params["youtubeDubLang"] = self.youtube_dub_lang
            
        # Remove None values
        return {k: v for k, v in params.items() if v is not None}
    
    def get_quality_fallback_list(self) -> list[str]:
        """Get list of video qualities to try, starting with preferred"""
        qualities = [self.video_quality.value]
        for fallback in self.video_quality_fallbacks:
            if fallback.value not in qualities:
                qualities.append(fallback.value)
        return qualities
    
    def get_codec_fallback_list(self) -> list[str]:
        """Get list of video codecs to try, starting with preferred"""
        codecs = [self.video_codec.value]
        for fallback in self.video_codec_fallbacks:
            if fallback.value not in codecs:
                codecs.append(fallback.value)
        return codecs
    
    def get_audio_fallback_list(self) -> list[str]:
        """Get list of audio formats to try, starting with preferred"""
        formats = [self.audio_format.value]
        for fallback in self.audio_format_fallbacks:
            if fallback.value not in formats:
                formats.append(fallback.value)
        return formats

@dataclass 
class DiscordConfig:
    """Configuration for Discord integration"""
    
    # File size limits based on server tier
    free_tier_limit: int = 8_388_608      # 8MB
    nitro_basic_limit: int = 26_214_400   # 25MB  
    nitro_limit: int = 104_857_600        # 100MB
    
    # Default to free tier
    current_limit: int = free_tier_limit
    
    # Upload settings
    upload_timeout: int = 60  # Seconds to wait for Discord upload
    compress_large_files: bool = True  # Try to compress files that are too large
    
@dataclass
class AppConfig:
    """Main application configuration"""
    
    # Component configurations
    cobalt: CobaltConfig = field(default_factory=CobaltConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    
    # General settings
    debug_mode: bool = False
    log_level: str = "INFO"
    temp_dir: str = "./video_temp_dir"
    downloads_dir: str = "./downloads"
    
    # Cleanup settings
    auto_cleanup: bool = True  # Automatically delete files after upload
    cleanup_age_hours: int = 24  # Delete temp files older than this
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables"""
        config = cls()
        
        # Cobalt settings
        if os.getenv("COBALT_API_URL"):
            config.cobalt.cobalt_instance_url = os.getenv("COBALT_API_URL")
        if os.getenv("VIDEO_QUALITY"):
            try:
                config.cobalt.video_quality = VideoQuality(os.getenv("VIDEO_QUALITY"))
            except ValueError:
                pass
        if os.getenv("VIDEO_CODEC"):
            try:
                config.cobalt.video_codec = VideoCodec(os.getenv("VIDEO_CODEC"))
            except ValueError:
                pass
        if os.getenv("MAX_FILE_SIZE"):
            try:
                config.cobalt.max_file_size = int(os.getenv("MAX_FILE_SIZE"))
            except ValueError:
                pass
        if os.getenv("MAX_FILE_SIZE_MB"):
            try:
                config.cobalt.max_file_size_mb = float(os.getenv("MAX_FILE_SIZE_MB"))
                # Trigger the conversion in __post_init__
                config.cobalt.__post_init__()
            except ValueError:
                pass
        if os.getenv("PICKER_BEHAVIOR"):
            try:
                config.cobalt.picker_behavior = PickerBehavior(os.getenv("PICKER_BEHAVIOR"))
            except ValueError:
                pass
                
        # Additional Cobalt settings
        if os.getenv("AUDIO_FORMAT"):
            try:
                config.cobalt.audio_format = AudioFormat(os.getenv("AUDIO_FORMAT"))
            except ValueError:
                pass
        if os.getenv("FILE_FORMAT"):
            try:
                config.cobalt.file_format = FileFormat(os.getenv("FILE_FORMAT"))
            except ValueError:
                pass
        if os.getenv("IS_AUDIO_ONLY"):
            config.cobalt.is_audio_only = os.getenv("IS_AUDIO_ONLY").lower() == "true"
        if os.getenv("TIKTOK_H265"):
            config.cobalt.tiktok_h265 = os.getenv("TIKTOK_H265").lower() == "true"
        if os.getenv("TWITTER_GIF"):
            config.cobalt.twitter_gif = os.getenv("TWITTER_GIF").lower() == "true"
        if os.getenv("YOUTUBE_DUB_LANG"):
            config.cobalt.youtube_dub_lang = os.getenv("YOUTUBE_DUB_LANG")
        if os.getenv("REQUEST_TIMEOUT"):
            try:
                config.cobalt.request_timeout = int(os.getenv("REQUEST_TIMEOUT"))
            except ValueError:
                pass
        if os.getenv("DOWNLOAD_TIMEOUT"):
            try:
                config.cobalt.download_timeout = int(os.getenv("DOWNLOAD_TIMEOUT"))
            except ValueError:
                pass
        if os.getenv("MAX_RETRIES"):
            try:
                config.cobalt.max_retries = int(os.getenv("MAX_RETRIES"))
            except ValueError:
                pass
                
        # Discord settings
        if os.getenv("DISCORD_FILE_LIMIT"):
            try:
                config.discord.current_limit = int(os.getenv("DISCORD_FILE_LIMIT"))
            except ValueError:
                pass
        if os.getenv("UPLOAD_TIMEOUT"):
            try:
                config.discord.upload_timeout = int(os.getenv("UPLOAD_TIMEOUT"))
            except ValueError:
                pass
                
        # General settings
        if os.getenv("DEBUG_MODE"):
            config.debug_mode = os.getenv("DEBUG_MODE").lower() == "true"
        if os.getenv("LOG_LEVEL"):
            config.log_level = os.getenv("LOG_LEVEL")
        if os.getenv("TEMP_DIR"):
            config.temp_dir = os.getenv("TEMP_DIR")
        if os.getenv("DOWNLOADS_DIR"):
            config.downloads_dir = os.getenv("DOWNLOADS_DIR")
        if os.getenv("AUTO_CLEANUP"):
            config.auto_cleanup = os.getenv("AUTO_CLEANUP").lower() == "true"
        if os.getenv("CLEANUP_AGE_HOURS"):
            try:
                config.cleanup_age_hours = int(os.getenv("CLEANUP_AGE_HOURS"))
            except ValueError:
                pass
            
        return config

# Global configuration instance
config = AppConfig.from_env()