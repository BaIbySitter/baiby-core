import logging
import asyncio
import importlib
import inspect

from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.state_manager import StateManager
from src.sentinels.base_sentinel import BaseSentinel
from contextlib import asynccontextmanager
from src.config import get_settings
from src.routers import api, rpc
from src.agent import BAIbyAgent

# Load environment variables from .env file
load_dotenv()

settings = get_settings()

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Store sentinel tasks and agent task to cancel them on shutdown
sentinel_tasks = []
agent_task = None

def discover_sentinels():
    """Dynamically discover and instantiate all sentinel classes"""
    sentinels = []
    sentinels_dir = Path(__file__).parent / "sentinels"
    
    for file in sentinels_dir.glob("*.py"):
        if file.stem in ["__init__", "base_sentinel"]:
            continue
            
        module_path = f"src.sentinels.{file.stem}"
        module = importlib.import_module(module_path)
        
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseSentinel) and 
                obj != BaseSentinel):
                sentinels.append(obj())
    
    return sentinels

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    state = StateManager()
    await state.init()
    
    # Initialize agent
    agent = BAIbyAgent()
    global agent_task
    agent_task = asyncio.create_task(agent.listen())
    logger.info(f"🤖 Agent activated: {agent.name}")
    
    # Discover and store sentinels
    sentinels = discover_sentinels()
    sentinel_names = {sentinel.name for sentinel in sentinels}
    await state.set_active_sentinels(sentinel_names)
    
    # Start sentinel tasks
    for sentinel in sentinels:
        task = asyncio.create_task(sentinel.listen())
        sentinel_tasks.append(task)
        logger.info(f"✅ Sentinel activated: {sentinel.name}")
    
    logger.info("🚀 Application started successfully")
    
    yield  # Application runs here
    
    # Shutdown
    if agent_task:
        agent_task.cancel()
        await asyncio.gather(agent_task, return_exceptions=True)
        
    for task in sentinel_tasks:
        task.cancel()
    await asyncio.gather(*sentinel_tasks, return_exceptions=True)
    
    await state.close()
    logger.info("Application and sentinels shutdown")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Usar variable de entorno
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los headers
)

# Include routers
app.include_router(api.router)
app.include_router(rpc.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT) 