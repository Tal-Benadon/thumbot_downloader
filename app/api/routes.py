from fastapi import APIRouter
from app.api.videos import router as videos_router

router = APIRouter()

router.include_router(videos_router, prefix="/videos", tags=["videos"])