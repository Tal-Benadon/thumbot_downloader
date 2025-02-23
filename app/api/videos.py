from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.downloader import proccess_video_request
import uuid

router = APIRouter()

class VideoRequest(BaseModel):
    url: str

tasks = {}

@router.get("/")
async def testingAPI(url: str):
    print(f"Received video link {url}")
    return {"message": f"get request arrived successfully with url {url}"}

@router.post("/")
async def download(video_req: VideoRequest, background_tasks: BackgroundTasks):
    
    task_id = str(uuid.uuid4)
    
    tasks[task_id] = {"status": "proccessing", "url": video_req.url}
    
    background_tasks.add_task(proccess_video_request, video_req.url, task_id)
    
    return {"message" : "Proccessing started", "task_id" :task_id}