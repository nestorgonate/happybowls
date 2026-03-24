from contextlib import asynccontextmanager
import os
from core import config
from fastapi import FastAPI
config.setupenv()
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
from core.dependencies import getLoadEmailService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
from endpoints import autenticacion
setupLogs()
loadEmails = getLoadEmailService()
logger = logging.getLogger("email_organizer")
base_dir = Path(__file__).resolve().parent
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        loadEmails.checkEmails,
        trigger="interval",
        minutes=5,
        max_instances=1,
        id="emailService_handleEmails",
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=1)
    )
    scheduler.start()
    for job in scheduler.get_jobs():
        logger.info(f"ID: {job.id} Tasks: {job.next_run_time}")
    yield
    scheduler.shutdown()
app = FastAPI(lifespan=lifespan)
app.include_router(router=agente.router)
app.include_router(router=dashboard.router)
app.include_router(router=emailclient.router)
app.include_router(router=autenticacion.router)
app.mount("/", StaticFiles(directory=base_dir/"dist", html=True), name="assets")
app.add_middleware(
    CORSMiddleware,
    #Cambiar despues para mejor seguridad
    allow_origins=["http://localhost:5173/"],
    allow_methods=["POST", "GET", "DELETE", "UPDATE"],
    allow_headers=["*"],
)
def main():
    multiprocessing.freeze_support()
    logger.info(msg="You can access your website at http://127.0.0.1:8000")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app=app, host="0.0.0.0", port=port)
if __name__ == "__main__":
    main()