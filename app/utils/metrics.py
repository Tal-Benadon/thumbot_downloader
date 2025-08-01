"""
Prometheus metrics for ThumbBot Downloader Service
"""
from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
import time
from functools import wraps
from typing import Optional, Callable, Any
import threading
from app.utils.logger import get_logger

logger = get_logger("metrics")

# Metrics definitions
download_requests_total = Counter(
    'thumbbot_download_requests_total', 
    'Total number of download requests',
    ['provider', 'status']
)

download_duration_seconds = Histogram(
    'thumbbot_download_duration_seconds',
    'Time spent downloading videos',
    ['provider'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0]
)

video_file_size_bytes = Histogram(
    'thumbbot_video_file_size_bytes',
    'Size of downloaded video files in bytes',
    ['provider'],
    buckets=[1024*100, 1024*500, 1024*1024, 1024*1024*5, 1024*1024*10, 
             1024*1024*25, 1024*1024*50, 1024*1024*100]
)

discord_uploads_total = Counter(
    'thumbbot_discord_uploads_total',
    'Total number of Discord uploads',
    ['status']
)

discord_upload_duration_seconds = Histogram(
    'thumbbot_discord_upload_duration_seconds',
    'Time spent uploading to Discord',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0]
)

cobalt_requests_total = Counter(
    'thumbbot_cobalt_requests_total',
    'Total number of requests to Cobalt API',
    ['instance', 'status']
)

cobalt_response_time_seconds = Histogram(
    'thumbbot_cobalt_response_time_seconds',
    'Cobalt API response time',
    ['instance'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

active_downloads = Gauge(
    'thumbbot_active_downloads',
    'Number of currently active downloads'
)

system_info = Info(
    'thumbbot_downloader_info',
    'Information about the ThumbBot downloader service'
)

# Metrics server
metrics_server_started = False
metrics_lock = threading.Lock()

def start_metrics_server(port: int = 8002):
    """Start Prometheus metrics server"""
    global metrics_server_started
    
    with metrics_lock:
        if not metrics_server_started:
            try:
                start_http_server(port)
                metrics_server_started = True
                logger.success(f"📊 Prometheus metrics server started on port {port}")
                
                # Set system info
                system_info.info({
                    'service': 'thumbbot-downloader',
                    'version': '2.0.0',
                    'python_version': '3.10+'
                })
                
            except Exception as e:
                logger.error(f"Failed to start metrics server: {e}")
        else:
            logger.debug("Metrics server already started")

def track_download_request(provider: str, status: str):
    """Track download request"""
    download_requests_total.labels(provider=provider, status=status).inc()

def track_download_duration(provider: str, duration: float):
    """Track download duration"""
    download_duration_seconds.labels(provider=provider).observe(duration)

def track_video_file_size(provider: str, size_bytes: int):
    """Track video file size"""
    video_file_size_bytes.labels(provider=provider).observe(size_bytes)

def track_discord_upload(status: str):
    """Track Discord upload"""
    discord_uploads_total.labels(status=status).inc()

def track_discord_upload_duration(duration: float):
    """Track Discord upload duration"""
    discord_upload_duration_seconds.observe(duration)

def track_cobalt_request(instance: str, status: str, response_time: float):
    """Track Cobalt API request"""
    cobalt_requests_total.labels(instance=instance, status=status).inc()
    cobalt_response_time_seconds.labels(instance=instance).observe(response_time)

class MetricsContext:
    """Context manager for tracking metrics"""
    
    def __init__(self, metric_name: str, labels: dict = None):
        self.metric_name = metric_name
        self.labels = labels or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        if self.metric_name == "active_downloads":
            active_downloads.inc()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if self.metric_name == "active_downloads":
            active_downloads.dec()
        
        if exc_type is None:
            # Success
            if self.metric_name == "download":
                track_download_duration(
                    self.labels.get('provider', 'unknown'), 
                    duration
                )
                track_download_request(
                    self.labels.get('provider', 'unknown'), 
                    'success'
                )
            elif self.metric_name == "discord_upload":
                track_discord_upload_duration(duration)
                track_discord_upload('success')
        else:
            # Error
            if self.metric_name == "download":
                track_download_request(
                    self.labels.get('provider', 'unknown'), 
                    'error'
                )
            elif self.metric_name == "discord_upload":
                track_discord_upload('error')

def metrics_decorator(metric_name: str, **labels):
    """Decorator for automatically tracking metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with MetricsContext(metric_name, labels):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Convenience functions
def with_download_metrics(provider: str):
    """Decorator for download functions"""
    return metrics_decorator("download", provider=provider)

def with_upload_metrics():
    """Decorator for upload functions"""
    return metrics_decorator("discord_upload")

def with_active_download_tracking():
    """Context manager for tracking active downloads"""
    return MetricsContext("active_downloads")