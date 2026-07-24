from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from repository.notification import NotificationRepo
from schema.assignment import Assignment
from schema.team import TeamMember
from schema.user import User as db_user
from schema.task import Task


class NotificationService:
    def __init__(self, db_session: AsyncSession = None):
        self.session = db_session

    async def get_my_notifications(self, current_user: db_user):
        sess = self.session
        return await NotificationRepo.get_user_notifications(current_user.id, sess)

    async def mark_read(self, notification_id: str, current_user: db_user):
        sess = self.session
        notification = await NotificationRepo.get_notification_by_id(notification_id, sess)
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot modify another user's notification",
            )
        return await NotificationRepo.mark_as_read(notification, sess)

    async def update_delivery_time(self, notification_id: str, delivered_at, current_user: db_user):
        sess = self.session
        notification = await NotificationRepo.get_notification_by_id(notification_id, sess)
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot modify another user's notification",
            )
        return await NotificationRepo.update_delivery_time(notification, delivered_at, sess)

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
        from repository.team import TeamRepo

        user_ids = await TeamRepo.get_member_ids_by_project(project_id, session)
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
        from repository.task import TaskCrud

        user_ids = await TaskCrud.get_assignee_ids_by_task(task_id, session)
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
        from repository.team import TeamRepo

        user_ids = await TeamRepo.get_member_ids_by_team(team_id, session)
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

    @staticmethod
    async def get_all_notifications(current_user: db_user, session: AsyncSession):
        return await NotificationRepo.get_user_notifications(current_user.id, session)
