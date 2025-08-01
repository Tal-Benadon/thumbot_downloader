"""
Enhanced logging system with colors and structured output for ThumbBot Downloader
"""
import sys
from loguru import logger
from typing import Optional
import os

class ThumbBotLogger:
    """Enhanced logger with colors and structured output"""
    
    def __init__(self, service_name: str = "thumbbot-downloader"):
        self.service_name = service_name
        self.setup_logger()
    
    def setup_logger(self):
        """Configure loguru with colors for stdout only"""
        
        # Remove default handler
        logger.remove()
        
        # Console handler with colors (stdout only)
        logger.add(
            sys.stdout,
            format=(
                "<level>{level: <8}</level> | <level>{message}</level>"
            ),
            level=os.getenv("LOG_LEVEL", "INFO"),
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    
    def get_logger(self, name: Optional[str] = None):
        """Get a logger instance with optional name"""
        if name:
            return logger.bind(name=name)
        return logger

# Global logger instance
thumbbot_logger = ThumbBotLogger()
get_logger = thumbbot_logger.get_logger

# Convenience functions
def log_request(method: str, url: str, status_code: Optional[int] = None):
    """Log HTTP requests with colors"""
    if status_code:
        if 200 <= status_code < 300:
            logger.success(f"{method} {url} -> {status_code}")
        elif 400 <= status_code < 500:
            logger.warning(f"{method} {url} -> {status_code}")
        else:
            logger.error(f"{method} {url} -> {status_code}")
    else:
        logger.info(f"{method} {url}")

def log_download_start(url: str, provider: str):
    """Log download start"""
    logger.info(f"🎬 Starting download from {provider}: {url}")

def log_download_success(url: str, file_size: str, duration: float):
    """Log successful download"""
    logger.success(f"✅ Download completed: {file_size} in {duration:.2f}s")

def log_download_error(url: str, error: str):
    """Log download error"""
    logger.error(f"❌ Download failed for {url}: {error}")

def log_upload_start(channel_id: str, filename: str):
    """Log Discord upload start"""
    logger.info(f"📤 Uploading {filename} to channel {channel_id}")

def log_upload_success(channel_id: str, filename: str):
    """Log successful Discord upload"""
    logger.success(f"✅ Uploaded {filename} to Discord channel {channel_id}")

def log_upload_error(channel_id: str, filename: str, error: str):
    """Log Discord upload error"""
    logger.error(f"❌ Upload failed for {filename} to channel {channel_id}: {error}")

def log_system_info(info: dict):
    """Log system information"""
    logger.info(f"🖥️  System Info: {info}")

def log_config_loaded(config_items: int):
    """Log configuration loading"""
    logger.success(f"⚙️  Configuration loaded: {config_items} items")