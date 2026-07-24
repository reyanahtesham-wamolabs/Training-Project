from datetime import date, timedelta
from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dependencies.database import AsyncSessionLocal
from schema.task import Task
from schema.assignment import Assignment
from schema.user import User as db_User
from schema.enums import ProjectStatus as Status
from services.notification_service import NotificationService
from helper_functions.opt_gen import send_task_due_reminder_email

scheduler = AsyncIOScheduler()


async def check_task_due_dates_and_notify():
    async with AsyncSessionLocal() as session:
        try:
            today = date.today()
            tomorrow = today + timedelta(days=1)

            # Query active, unfinished tasks with due_date within 1 day (today or tomorrow)
            stmt = select(Task).where(
                Task.soft_delete == False,
                Task.status != Status.finished,
                Task.due_date != None,
                Task.due_date <= tomorrow,
                Task.due_reminder_sent == False
            )
            result = await session.execute(stmt)
            due_tasks = result.scalars().all()

            for task in due_tasks:
                # Query assignments for this task
                assign_stmt = select(Assignment).where(Assignment.task_id == task.id)
                assign_res = await session.execute(assign_stmt)
                assignments = assign_res.scalars().all()

                for ass in assignments:
                    user = await session.get(db_User, ass.user_id)
                    if user and user.email:
                        # 1. Send Email to assigned user
                        await send_task_due_reminder_email(
                            email=user.email,
                            task_name=task.name,
                            due_date_str=str(task.due_date),
                            project_name=task.project_id
                        )

                        # 2. Send In-App Notification to assigned user
                        await NotificationService.notify_user(
                            user_id=user.id,
                            subject="⏰ Task Due Reminder (< 1 Day)",
                            text=f"Your assigned task '{task.name}' has less than 1 day left before its due date ({task.due_date}).",
                            session=session,
                            related_task_id=task.id,
                            related_project_id=task.project_id
                        )

                # Mark reminder sent on task so emails aren't duplicated on subsequent intervals
                task.due_reminder_sent = True
                session.add(task)

            await session.commit()
        except Exception as e:
            print(f"[Scheduler Error] Failed to check task due dates: {e}")


scheduler.add_job(
    check_task_due_dates_and_notify,
    trigger="interval",
    seconds=60,
)
