from contextlib import asynccontextmanager
from core import config
from fastapi import FastAPI
config.setupenv()
from tasks.backgroundtask import StartScheduler
from endpoints import agente
from endpoints import dashboard
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import multiprocessing
import logging
from core.logs import setupLogs
from endpoints import emailclient
setupLogs()
logger = logging.getLogger("email_organizer")
@asynccontextmanager
async def lifespan(app: FastAPI):
    await StartScheduler()
    yield
base_dir = Path(__file__).resolve().parent
app = FastAPI(lifespan=lifespan)
app.include_router(router=agente.router)
app.include_router(router=dashboard.router)
app.include_router(router=emailclient.router)
app.mount("/", StaticFiles(directory=base_dir/"dist", html=True), name="assets")
app.add_middleware(
    CORSMiddleware,
    #Cambiar despues para mejor seguridad
    allow_origins=["http://localhost:5173/"],
    allow_methods=["POST", "GET", "DELETE", "UPDATE"],
    allow_headers=["*"],
)
if __name__ == "__main__":
    multiprocessing.freeze_support()
    logger.info(msg="You can access your website at http://127.0.0.1:8000")
    uvicorn.run(app=app, host="127.0.0.1", port=8000)