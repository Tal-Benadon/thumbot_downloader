from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.downloader import proccess_video_request
import uuid

router = APIRouter()

class VideoRequest(BaseModel):
    url: str
    channelId: str
    
# tasks = {}


@router.get("")
async def testingAPI(url: str):
    print(f"Received video link {url}")
    return {"message": f"get request arrived successfully with url {url}"}

# background_tasks: BackgroundTasks
@router.post("")
async def download(video_req: VideoRequest ):
    
    print(video_req.channelId)
    print(video_req.url)
  
    final_response = proccess_video_request(video_req.url, video_req.channelId)
    
    return {"message" : f"{final_response}"}

  
    # task_id = str(uuid.uuid4)
    
    # tasks[task_id] = {"status": "proccessing", "url": video_req.url}
    
    # background_tasks.add_task(proccess_video_request, video_req.url, task_id)
    # , "task_id" :task_id