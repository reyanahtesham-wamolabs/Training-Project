from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from repository.comment import CommentCrud
from repository.task import TaskCrud
from schema.comment import Comment as db_Comment
from schema.enums import Roles
from models.comment_models import CommentCreate, CommentUpdate
from services.notification_service import NotificationService

class CommentService:

    @staticmethod
    async def create_comment(
        data: CommentCreate, current_user, session: AsyncSession
    ) -> db_Comment:
        task = await TaskCrud.get_task_by_id(data.task_id, session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{data.task_id}' not found",
            )

        is_assigned = await CommentCrud.is_user_in_project(current_user.id, task.project_id, session)
        if not is_assigned and current_user.role != Roles.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project",
            )

        if data.parent_comment_id:
            parent_comment = await CommentCrud.get_comment_by_id(data.parent_comment_id, session)
            if parent_comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent comment with id '{data.parent_comment_id}' not found",
                )
            if parent_comment.task_id != data.task_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment does not belong to the same task",
                )
            if parent_comment.parent_comment_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Replies can only be made to top-level comments",
                )
            from sqlalchemy import select, exists
            stmt = select(exists().where(db_Comment.parent_comment_id == data.parent_comment_id))
            result = await session.execute(stmt)
            has_reply = result.scalar()
            if has_reply:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This comment already has a reply",
                )

        try:
            comment = await CommentCrud.add_comment(data, current_user.id, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment due to a database error",
            ) from e

        # Pre-load user relationship for returned object / notifications
        comment = await CommentCrud.get_comment_by_id(comment.id, session)

        try:
            if data.parent_comment_id:
                # Notify the parent comment's author
                if parent_comment.user_id != current_user.id:
                    await NotificationService.notify_user(
                        user_id=parent_comment.user_id,
                        subject="New Reply",
                        text=f"{current_user.name} replied to your comment on task '{task.name}'.",
                        session=session,
                        related_task_id=task.id,
                        related_comment_id=comment.id,
                        related_project_id=task.project_id
                    )
            else:
                # Notify task assignees
                await NotificationService.notify_task_assignees(
                    task_id=task.id,
                    subject="New Comment",
                    text=f"New comment added on task '{task.name}' by {current_user.name}.",
                    session=session,
                    exclude_user_id=current_user.id,
                    related_task_id=task.id,
                    related_comment_id=comment.id,
                    related_project_id=task.project_id
                )
        except Exception:
            # Prevent notification error from breaking creation flow
            pass

        return comment

    @staticmethod
    async def update_comment(
        comment_id: str, data: CommentUpdate, current_user, session: AsyncSession
    ) -> db_Comment:
        comment = await CommentCrud.get_comment_by_id(comment_id, session)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with id '{comment_id}' not found",
            )

        if comment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments",
            )

        try:
            return await CommentCrud.update_comment(comment, data.content, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment due to a database error",
            ) from e

    @staticmethod
    async def delete_comment(
        comment_id: str, current_user, session: AsyncSession
    ) -> None:
        comment = await CommentCrud.get_comment_by_id(comment_id, session)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with id '{comment_id}' not found",
            )

        task = await TaskCrud.get_task_by_id(comment.task_id, session)
        is_padmin = False
        if task:
            is_padmin = await CommentCrud.is_project_admin(current_user.id, task.project_id, session)

        can_delete = (
            comment.user_id == current_user.id
            or current_user.role == Roles.admin
            or is_padmin
        )

        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this comment",
            )

        try:
            await CommentCrud.delete_comment(comment_id, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment due to a database error",
            ) from e

    @staticmethod
    async def get_task_comments(
        task_id: str, current_user, session: AsyncSession
    ) -> list[db_Comment]:
        task = await TaskCrud.get_task_by_id(task_id, session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found",
            )

        is_assigned = await CommentCrud.is_user_in_project(current_user.id, task.project_id, session)
        if not is_assigned and current_user.role != Roles.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project",
            )

        try:
            return await CommentCrud.get_task_comments(task_id, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch comments due to a database error",
            ) from e
