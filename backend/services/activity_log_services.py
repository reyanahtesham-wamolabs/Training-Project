from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schema.activity_log import ActivityLog as db_ActivityLog
from schema.enums import ActivityActionType
from datetime import datetime, timezone
import uuid


class ActivityLogService:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def log_activity(
        self,
        modified_by_user_id: str,
        action_type: ActivityActionType,
        message: str,
        target_user_id: str | None = None,
        task_id: str | None = None,
        project_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> db_ActivityLog:
        db = session or self.session
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
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry

    @staticmethod
    async def log_activity_static(
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

    async def get_all_logs(self) -> list[db_ActivityLog]:
        stmt = select(db_ActivityLog).order_by(db_ActivityLog.change_time.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_own_logs(self, current_user) -> list[db_ActivityLog]:
        stmt = (
            select(db_ActivityLog)
            .where(db_ActivityLog.modified_by_user_id == current_user.id)
            .order_by(db_ActivityLog.change_time.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
