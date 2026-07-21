from __future__ import annotations
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schema.task import Task as db_Task
from schema.team import Team as db_Team, TeamMember as db_TeamMember
from schema.comment import Comment as db_Comment
from schema.assignment import Assignment as db_Assignment
from schema.enums import AssignmentRole
from models.comment_models import CommentCreate, CommentUpdate
import uuid

class CommentCrud:

    @staticmethod
    async def add_comment(data: CommentCreate, user_id: str, session: AsyncSession) -> db_Comment:
        comment = db_Comment(
            id=str(uuid.uuid4()),
            content=data.content,
            user_id=user_id,
            task_id=data.task_id,
            parent_comment_id=data.parent_comment_id,
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

    @staticmethod
    async def get_comment_by_id(comment_id: str, session: AsyncSession) -> db_Comment | None:
        stmt = (
            select(db_Comment)
            .options(
                selectinload(db_Comment.user),
                selectinload(db_Comment.reply).selectinload(db_Comment.user),
            )
            .where(db_Comment.id == comment_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_task_comments(task_id: str, session: AsyncSession) -> list[db_Comment]:
        stmt = (
            select(db_Comment)
            .options(
                selectinload(db_Comment.user),
                selectinload(db_Comment.reply).selectinload(db_Comment.user),
            )
            .where(db_Comment.task_id == task_id)
            .where(db_Comment.parent_comment_id == None)
            .order_by(db_Comment.created_at.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_comment(comment_id: str, session: AsyncSession) -> bool:
        comment = await session.get(db_Comment, comment_id)
        if comment is None:
            return False
        await session.delete(comment)
        await session.commit()
        return True

    @staticmethod
    async def update_comment(comment: db_Comment, content: str, session: AsyncSession) -> db_Comment:
        comment.content = content
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment
      
    @staticmethod
    async def is_user_in_project(user_id: str, project_id: str, session: AsyncSession) -> bool:
        """Check if a user is a member of the team belonging to the given project."""
        stmt = select(exists().where(
            db_TeamMember.user_id == user_id,
            db_TeamMember.team_id.in_(
                select(db_Team.id).where(db_Team.project_id == project_id)
            )
        ))
        result = await session.execute(stmt)
        return bool(result.scalar())

    @staticmethod
    async def is_project_admin(user_id: str, project_id: str, session: AsyncSession) -> bool:
        """Check if a user holds the project_admin role on any task in the given project."""
        stmt = select(exists().where(
            db_Assignment.user_id == user_id,
            db_Assignment.role == AssignmentRole.project_admin,
            db_Assignment.task_id.in_(
                select(db_Task.id).where(db_Task.project_id == project_id)
            )
        ))
        result = await session.execute(stmt)
        return bool(result.scalar())

