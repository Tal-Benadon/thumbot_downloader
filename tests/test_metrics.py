"""
Tests for ThumbBot Downloader metrics system
"""
import pytest
import sys
import os
import time

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.metrics import (
    track_download_request, track_download_duration, track_video_file_size,
    track_discord_upload, track_discord_upload_duration, track_cobalt_request,
    MetricsContext, with_download_metrics, with_upload_metrics
)

class TestMetricsTracking:
    """Test metrics tracking functions"""
    
    def test_track_download_request(self):
        """Test download request tracking"""
        # Should not raise exceptions
        track_download_request("instagram", "success")
        track_download_request("reddit", "error")
    
    def test_track_download_duration(self):
        """Test download duration tracking"""
        track_download_duration("instagram", 1.5)
        track_download_duration("reddit", 0.8)
    
    def test_track_video_file_size(self):
        """Test video file size tracking"""
        track_video_file_size("instagram", 1024 * 1024)  # 1MB
        track_video_file_size("reddit", 5 * 1024 * 1024)  # 5MB
    
    def test_track_discord_upload(self):
        """Test Discord upload tracking"""
        track_discord_upload("success")
        track_discord_upload("error")
    
    def test_track_discord_upload_duration(self):
        """Test Discord upload duration tracking"""
        track_discord_upload_duration(2.3)
    
    def test_track_cobalt_request(self):
        """Test Cobalt request tracking"""
        track_cobalt_request("localhost:9000", "success", 0.5)
        track_cobalt_request("api.cobalt.tools", "error", 1.2)

class TestMetricsContext:
    """Test metrics context manager"""
    
    def test_metrics_context_success(self):
        """Test metrics context for successful operations"""
        with MetricsContext("download", {"provider": "instagram"}):
            time.sleep(0.01)  # Simulate some work
            # Context should track this as success
    
    def test_metrics_context_error(self):
        """Test metrics context for failed operations"""
        try:
            with MetricsContext("discord_upload"):
                time.sleep(0.01)
                raise Exception("Test error")
        except Exception:
            pass  # Expected
    
    def test_active_download_tracking(self):
        """Test active download tracking"""
        from app.utils.metrics import with_active_download_tracking
        
        with with_active_download_tracking():
            time.sleep(0.01)
            # Should increment and decrement active downloads counter

class TestMetricsDecorators:
    """Test metrics decorators"""
    
    def test_download_metrics_decorator(self):
        """Test download metrics decorator"""
        @with_download_metrics("instagram")
        def test_download():
            time.sleep(0.01)
            return "success"
        
        result = test_download()
        assert result == "success"
    
    def test_upload_metrics_decorator(self):
        """Test upload metrics decorator"""
        @with_upload_metrics()
        def test_upload():
            time.sleep(0.01)
            return "uploaded"
        
        result = test_upload()
        assert result == "uploaded"
    
    def test_decorator_with_exception(self):
        """Test decorator behavior with exceptions"""
        @with_download_metrics("test")
        def failing_download():
            raise Exception("Download failed")
        
        with pytest.raises(Exception):
            failing_download()

class TestMetricsServer:
    """Test metrics server functionality"""
    
    def test_metrics_server_start(self):
        """Test metrics server can be started"""
        from app.utils.metrics import start_metrics_server
        
        # Should not crash (may fail if port is in use, but shouldn't crash)
        try:
            start_metrics_server(8003)  # Use different port for testing
        except Exception as e:
            # Only fail if it's not a "port in use" error
            if "Address already in use" not in str(e):
                raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])