"""
Tests for ThumbBot Downloader logging system
"""
import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.logger import ThumbBotLogger, get_logger
from app.utils.logger import log_download_start, log_download_success, log_download_error
from app.utils.logger import log_upload_start, log_upload_success, log_upload_error

class TestThumbBotLogger:
    """Test the ThumbBot logger functionality"""
    
    def test_logger_initialization(self):
        """Test logger initializes correctly"""
        logger = ThumbBotLogger("test-service")
        assert logger.service_name == "test-service"
    
    def test_get_logger_function(self):
        """Test get_logger convenience function"""
        logger = get_logger("test-module")
        assert logger is not None
    
    def test_log_functions_dont_crash(self):
        """Test that all log functions can be called without crashing"""
        # These should not raise exceptions
        log_download_start("https://example.com", "instagram")
        log_download_success("https://example.com", "1.5MB", 2.5)
        log_download_error("https://example.com", "Network error")
        
        log_upload_start("123456", "video.mp4")
        log_upload_success("123456", "video.mp4")
        log_upload_error("123456", "video.mp4", "Upload failed")

class TestLoggerConfiguration:
    """Test logger configuration for stdout only"""
    
    def test_logger_stdout_only(self):
        """Test that logger uses stdout only (no file logging)"""
        # Check that logs directory is not created
        logs_dir = Path("logs")
        
        # Initialize logger
        get_logger("test")  # This should trigger logger initialization
        
        # Should not create logs directory since we're using stdout only
        assert not logs_dir.exists()  # If we got here, logger initialization worked without files

class TestLoggerIntegration:
    """Test logger integration with other components"""
    
    def test_logger_with_metrics(self):
        """Test that logger works with metrics"""
        from app.utils.logger import log_system_info, log_config_loaded
        
        # These should not raise exceptions
        log_system_info({"cpu": "test", "memory": "1GB"})
        log_config_loaded(5)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])