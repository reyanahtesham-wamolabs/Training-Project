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
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create_comment(
        self, data: CommentCreate, current_user
    ) -> db_Comment:
        if current_user.is_external:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External collaborators cannot create comments",
            )
        task = await TaskCrud.get_task_by_id(data.task_id, self.session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{data.task_id}' not found",
            )

        is_assigned = await CommentCrud.is_user_in_project(current_user.id, task.project_id, self.session)
        if not is_assigned and current_user.role != Roles.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project",
            )

        if data.parent_comment_id:
            parent_comment = await CommentCrud.get_comment_by_id(data.parent_comment_id, self.session)
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
            # Flatten nesting: attach replies on replies to top-level parent comment
            if parent_comment.parent_comment_id is not None:
                data.parent_comment_id = parent_comment.parent_comment_id

        try:
            comment = await CommentCrud.add_comment(data, current_user.id, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment due to a database error",
            ) from e

        comment = await CommentCrud.get_comment_by_id(comment.id, self.session)

        try:
            if data.parent_comment_id:
                if parent_comment.user_id != current_user.id:
                    await NotificationService.notify_user(
                        user_id=parent_comment.user_id,
                        subject="New Reply",
                        text=f"{current_user.name} replied to your comment on task '{task.name}'.",
                        session=self.session,
                        related_task_id=task.id,
                        related_comment_id=comment.id,
                        related_project_id=task.project_id
                    )
            else:
                await NotificationService.notify_task_assignees(
                    task_id=task.id,
                    subject="New Comment",
                    text=f"New comment added on task '{task.name}' by {current_user.name}.",
                    session=self.session,
                    exclude_user_id=current_user.id,
                    related_task_id=task.id,
                    related_comment_id=comment.id,
                    related_project_id=task.project_id
                )
        except Exception:
            pass

        return comment

    async def update_comment(
        self, comment_id: str, data: CommentUpdate, current_user
    ) -> db_Comment:
        comment = await CommentCrud.get_comment_by_id(comment_id, self.session)
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
            return await CommentCrud.update_comment(comment, data.content, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment due to a database error",
            ) from e

    async def delete_comment(
        self, comment_id: str, current_user
    ) -> None:
        comment = await CommentCrud.get_comment_by_id(comment_id, self.session)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with id '{comment_id}' not found",
            )

        task = await TaskCrud.get_task_by_id(comment.task_id, self.session)
        is_padmin = False
        if task:
            is_padmin = await CommentCrud.is_project_admin(current_user.id, task.project_id, self.session)

        user_role = str(getattr(current_user.role, 'value', current_user.role)).lower()
        is_overall_admin_or_manager = user_role in ['admin', 'manager']
        can_delete = (
            comment.user_id == current_user.id
            or is_overall_admin_or_manager
            or is_padmin
        )

        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this comment",
            )

        try:
            await CommentCrud.delete_comment(comment_id, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment due to a database error",
            ) from e

    async def get_task_comments(
        self, task_id: str, current_user
    ) -> list[db_Comment]:
        task = await TaskCrud.get_task_by_id(task_id, self.session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found",
            )

        is_assigned = await CommentCrud.is_user_in_project(current_user.id, task.project_id, self.session)
        if not is_assigned and current_user.role != Roles.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project",
            )

        try:
            return await CommentCrud.get_task_comments(task_id, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch comments due to a database error",
            ) from e
