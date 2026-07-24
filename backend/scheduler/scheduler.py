from datetime import datetime, timezone, date, timedelta
from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dependencies.database import AsyncSessionLocal
from services.task_reminder import TaskReminderService
from services.task import TaskService
import subprocess
import os
from dotenv import load_dotenv
from helper_functions.logger import logging

load_dotenv()

PGPASSWORD = os.getenv("PGPASSWORD")
PGUSERNAME = os.getenv("PGUSERNAME")
PGDB = os.getenv("PGDB")
scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)


async def backup_db():
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = PGPASSWORD

        day_of_month = date.today().day
        backup_filename = f"{day_of_month}_backup.dump"

        subprocess.run(
            [
                "pg_dump",
                "-h",
                "localhost",
                "-U",
                PGUSERNAME,
                "-d",
                PGDB,
                "-F",
                "c",
                "-f",
                backup_filename,
            ],
            env=env,
            check=True,
        )

    except Exception as e:
        logger.error(f"The daily database backup has failed {e}")


async def check_task_due_dates_and_notify():
    async with AsyncSessionLocal() as session:
        await TaskService.process_due_date_reminders(session)

async def process_recurring_reminders():
    async with AsyncSessionLocal() as session:
        await TaskReminderService.process_due_reminders(session)


scheduler.add_job(
    check_task_due_dates_and_notify,
    trigger="interval",
    seconds=360,
)
scheduler.add_job(
    process_recurring_reminders,
    trigger="interval",
    seconds=120,  # check every 2 minutes
)
scheduler.add_job(
    backup_db,
    trigger="cron",
    day="*",
    hour=1,
    minute=0,
)
