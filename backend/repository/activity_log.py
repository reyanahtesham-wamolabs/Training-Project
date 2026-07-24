from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schema.activity_log import ActivityLog as db_ActivityLog
from schema.enums import ActivityActionType
from datetime import datetime, timezone
import uuid

class ActivityLogRepo:
    @staticmethod
    async def create_log(
        session: AsyncSession,
        modified_by_user_id: str,
        action_type: ActivityActionType,
        message: str,
        target_user_id: str | None = None,
        task_id: str | None = None,
        project_id: str | None = None,
    ) -> db_ActivityLog:
        log_entry = db_ActivityLog(
            id=str(uuid.uuid4()),
            modified_by_user_id=modified_by_user_id,
            target_user_id=target_user_id,
            task_id=task_id,
            project_id=project_id,
            action_type=action_type,
            message=message,
            change_time=datetime.now(timezone.utc),
        )
        session.add(log_entry)
        await session.commit()
        await session.refresh(log_entry)
        return log_entry

    @staticmethod
    async def get_all_logs(session: AsyncSession) -> list[db_ActivityLog]:
        stmt = select(db_ActivityLog).order_by(db_ActivityLog.change_time.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_logs_by_user(user_id: str, session: AsyncSession) -> list[db_ActivityLog]:
        stmt = (
            select(db_ActivityLog)
            .where(db_ActivityLog.modified_by_user_id == user_id)
            .order_by(db_ActivityLog.change_time.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
