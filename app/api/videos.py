from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.downloader import proccess_video_request
from app.utils.logger import get_logger
from app.utils.metrics import track_download_request, MetricsContext
import time

router = APIRouter()
logger = get_logger("videos_api")

class VideoRequest(BaseModel):
    url: HttpUrl
    channelId: str

class VideoResponse(BaseModel):
    status: str
    message: str
    request_id: str
    timestamp: float

@router.post("", response_model=VideoResponse)
async def download(video_req: VideoRequest):
    """Process video download request"""
    request_id = str(int(time.time() * 1000))
    start_time = time.time()
    
    logger.info(f"🎬 New video request: {video_req.url}")
    logger.debug(f"Request ID: {request_id}, Channel: {video_req.channelId}")
    
    try:
        # Use metrics context to track the request
        with MetricsContext("download"):
            # Process the video request
            result = proccess_video_request(str(video_req.url), video_req.channelId)
            
            duration = time.time() - start_time
            logger.success(f"✅ Video request processed in {duration:.2f}s")
            
            return VideoResponse(
                status="success",
                message="Video download request processed successfully",
                request_id=request_id,
                timestamp=time.time()
            )
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ Video request failed after {duration:.2f}s: {str(e)}")
        
        # Track error in metrics
        track_download_request("unknown", "error")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to process video request",
                "message": str(e),
                "request_id": request_id,
                "timestamp": time.time()
            }
        )
