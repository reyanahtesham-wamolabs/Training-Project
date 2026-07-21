from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from repository.notification_repository import NotificationRepo
from schema.assignment import Assignment
from schema.team import TeamMember

class NotificationService:

    @staticmethod
    async def notify_user(
        user_id: str,
        subject: str,
        text: str,
        session: AsyncSession,
        related_task_id: str | None = None,
        related_comment_id: str | None = None,
        related_project_id: str | None = None,
        related_message_id: str | None = None,
    ):
        await NotificationRepo.create_notification(
            user_id=user_id,
            subject=subject,
            text=text,
            session=session,
            related_task_id=related_task_id,
            related_comment_id=related_comment_id,
            related_project_id=related_project_id,
            related_message_id=related_message_id,
        )

    @staticmethod
    async def notify_users(
        user_ids: list[str],
        subject: str,
        text: str,
        session: AsyncSession,
        exclude_user_id: str | None = None,
        related_task_id: str | None = None,
        related_comment_id: str | None = None,
        related_project_id: str | None = None,
        related_message_id: str | None = None,
    ):
        for uid in set(user_ids):
            if exclude_user_id and uid == exclude_user_id:
                continue
            await NotificationService.notify_user(
                user_id=uid,
                subject=subject,
                text=text,
                session=session,
                related_task_id=related_task_id,
                related_comment_id=related_comment_id,
                related_project_id=related_project_id,
                related_message_id=related_message_id,
            )

    @staticmethod
    async def notify_project_members(
        project_id: str,
        subject: str,
        text: str,
        session: AsyncSession,
        exclude_user_id: str | None = None,
        related_task_id: str | None = None,
        related_comment_id: str | None = None,
        related_project_id: str | None = None,
        related_message_id: str | None = None,
    ):
        stmt = select(Assignment.user_id).where(Assignment.project_id == project_id)
        result = await session.execute(stmt)
        user_ids = [row[0] for row in result.all() if row[0] is not None]
        await NotificationService.notify_users(
            user_ids=user_ids,
            subject=subject,
            text=text,
            session=session,
            exclude_user_id=exclude_user_id,
            related_task_id=related_task_id,
            related_comment_id=related_comment_id,
            related_project_id=related_project_id or project_id,
            related_message_id=related_message_id,
        )

    @staticmethod
    async def notify_task_assignees(
        task_id: str,
        subject: str,
        text: str,
        session: AsyncSession,
        exclude_user_id: str | None = None,
        related_task_id: str | None = None,
        related_comment_id: str | None = None,
        related_project_id: str | None = None,
        related_message_id: str | None = None,
    ):
        stmt = select(Assignment.user_id).where(Assignment.task_id == task_id)
        result = await session.execute(stmt)
        user_ids = [row[0] for row in result.all() if row[0] is not None]
        await NotificationService.notify_users(
            user_ids=user_ids,
            subject=subject,
            text=text,
            session=session,
            exclude_user_id=exclude_user_id,
            related_task_id=related_task_id or task_id,
            related_comment_id=related_comment_id,
            related_project_id=related_project_id,
            related_message_id=related_message_id,
        )

    @staticmethod
    async def notify_team_members(
        team_id: str,
        subject: str,
        text: str,
        session: AsyncSession,
        exclude_user_id: str | None = None,
        related_task_id: str | None = None,
        related_comment_id: str | None = None,
        related_project_id: str | None = None,
        related_message_id: str | None = None,
    ):
        stmt = select(TeamMember.user_id).where(TeamMember.team_id == team_id)
        result = await session.execute(stmt)
        user_ids = [row[0] for row in result.all() if row[0] is not None]
        await NotificationService.notify_users(
            user_ids=user_ids,
            subject=subject,
            text=text,
            session=session,
            exclude_user_id=exclude_user_id,
            related_task_id=related_task_id,
            related_comment_id=related_comment_id,
            related_project_id=related_project_id,
            related_message_id=related_message_id,
        )
