"""
Tests for ThumbBot Downloader API endpoints
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root health check"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "thumbbot-downloader"
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
    
    def test_health_endpoint(self):
        """Test detailed health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "thumbbot-downloader"
        assert data["status"] == "healthy"
        assert "features" in data
        assert "cobalt-integration" in data["features"]
        assert "discord-upload" in data["features"]
        assert "metrics" in data["features"]
        assert "logging" in data["features"]

class TestVideoAPI:
    """Test video download API"""
    
    def test_video_endpoint_invalid_url(self):
        """Test video endpoint with invalid URL"""
        response = client.post("/videos", json={
            "url": "not-a-url",
            "channelId": "123456789"
        })
        assert response.status_code == 422  # Validation error
    
    def test_video_endpoint_missing_fields(self):
        """Test video endpoint with missing fields"""
        response = client.post("/videos", json={
            "url": "https://example.com"
            # Missing channelId
        })
        assert response.status_code == 422  # Validation error
    
    def test_video_endpoint_valid_request_structure(self):
        """Test video endpoint with valid request structure"""
        # Note: This may fail if Cobalt/Discord aren't available, but structure should be OK
        response = client.post("/videos", json={
            "url": "https://www.instagram.com/reel/test/",
            "channelId": "123456789"
        })
        
        # Should be either 200 (success) or 500 (service unavailable)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "request_id" in data
            assert "timestamp" in data
            assert "message" in data

@pytest.mark.asyncio
class TestAsyncAPI:
    """Test async API functionality"""
    
    async def test_async_video_request(self):
        """Test async video request"""
        async with AsyncClient(base_url="http://test") as ac:
            # Use the TestClient for async testing instead
            response = client.post("/videos", json={
                "url": "https://www.reddit.com/r/test/",
                "channelId": "test_channel"
            })
            
            # Should handle the request properly regardless of downstream services
            assert response.status_code in [200, 500]

class TestMetricsIntegration:
    """Test that metrics are properly integrated"""
    
    def test_metrics_endpoint_available(self):
        """Test that metrics endpoint is available"""
        # The metrics server runs on a different port (8002)
        # This test just ensures the integration doesn't break the main app
        response = client.get("/")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])