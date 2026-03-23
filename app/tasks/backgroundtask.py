from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from app.core.dependencies import getLoadEmailService
loadEmails = getLoadEmailService()
async def StartScheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        loadEmails.checkEmails,
        trigger="interval",
        minutes=5,
        max_instances=1,
        id="emailService_handleEmails",
        next_run_time=datetime.now()
    )
    scheduler.start()