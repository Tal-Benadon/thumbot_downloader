from fastapi import APIRouter
from pydantic import BaseModel
from app.services.downloader import proccess_video_request

router = APIRouter()

class VideoRequest(BaseModel):
    url: str
    channelId: str

@router.post("")
async def download(video_req: VideoRequest ):
    
  
  
    proccess_video_request(video_req.url, video_req.channelId)
    
    return {"request processed"} # // need to decide if to return something, and if so, what?

  
