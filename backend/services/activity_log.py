from sqlalchemy.ext.asyncio import AsyncSession
from repository.activity_log import ActivityLogRepo
from schema.activity_log import ActivityLog as db_ActivityLog
from schema.enums import ActivityActionType


class ActivityLogService:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

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
        return await ActivityLogRepo.create_log(
            session=session,
            modified_by_user_id=modified_by_user_id,
            action_type=action_type,
            message=message,
            target_user_id=target_user_id,
            task_id=task_id,
            project_id=project_id,
        )

    async def get_all_logs(self) -> list[db_ActivityLog]:
        return await ActivityLogRepo.get_all_logs(self.session)

    async def get_own_logs(self, current_user) -> list[db_ActivityLog]:
        return await ActivityLogRepo.get_logs_by_user(current_user.id, self.session)
