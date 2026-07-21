from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema.notification import Notification as db_Notification

class NotificationRepo:

    @staticmethod
    async def create_notification(
        user_id: str,
        subject: str,
        text: str,
        session: AsyncSession,
        related_task_id: str | None = None,
        related_comment_id: str | None = None,
        related_project_id: str | None = None,
        related_message_id: str | None = None,
    ) -> db_Notification:
        notification = db_Notification(
            user_id=user_id,
            subject=subject,
            text=text,
            related_task_id=related_task_id,
            related_comment_id=related_comment_id,
            related_project_id=related_project_id,
            related_message_id=related_message_id,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    @staticmethod
    async def get_user_notifications(user_id: str, session: AsyncSession) -> list[db_Notification]:
        stmt = (
            select(db_Notification)
            .where(db_Notification.user_id == user_id)
            .order_by(db_Notification.delivered.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_notification_by_id(notification_id: str, session: AsyncSession) -> db_Notification | None:
        return await session.get(db_Notification, notification_id)

    @staticmethod
    async def mark_as_read(notification: db_Notification, session: AsyncSession) -> db_Notification:
        notification.read = True
        notification.read_at = datetime.now(timezone.utc)
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification
