from fastapi import FastAPI
from src.config import get_settings
from src.routers import api, rpc
import logging
import asyncio
from src.core import core

settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Include routers
app.include_router(api.router)
app.include_router(rpc.router)

@app.on_event("startup")
async def startup_event():
    await core.connect()

@app.on_event("shutdown")
async def shutdown_event():
    if core.redis:
        await core.redis.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT) 