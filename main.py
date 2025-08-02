from fastapi import FastAPI
from app.api.routes import router 
from app.utils.metrics import start_metrics_server
import uvicorn 
import asyncio

app = FastAPI()

app.include_router(router)

@app.get("/")
async def root():
    return {"start":"start"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Start metrics server on application startup"""
    start_metrics_server(8002)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8001, reload=True)