from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schema.assignment import Assignment as db_Assignment
from schema.user import User as db_User
from schema.team import Team as db_Team, TeamMember as db_TeamMember
from schema.task import Task as db_task
from models.task_models import Task, TaskCreation, TaskUpdate
from schema.enums import Levels, Roles


class TaskCrud:

    @staticmethod
    async def add_task(data: TaskCreation, session: AsyncSession) -> db_task:
        complete_task = Task(**data.model_dump())
        created_task = db_task(**complete_task.model_dump())
        session.add(created_task)
        await session.commit()
        await session.refresh(created_task)
        return created_task

    @staticmethod
    async def get_task_by_name(
        task_name: str, project_id: str, session: AsyncSession
    ) -> db_task | None:
        stmt = (
            select(db_task)
            .where(db_task.name == task_name)
            .where(db_task.project_id == project_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_task_by_id(task_id: str, session: AsyncSession) -> db_task | None:
        return await session.get(db_task, task_id)

    @staticmethod
    async def delete_task(task_id: str, session: AsyncSession) -> bool:
        task = await session.get(db_task, task_id)
        if task is None:
            return False
        await session.delete(task)
        await session.commit()
        return True

    @staticmethod
    async def update_task(data: TaskUpdate, session: AsyncSession) -> db_task | None:
        task = await session.get(db_task, data.id)
        if task is None:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"id"})
        for field, value in update_data.items():
            setattr(task, field, value)

        await session.commit()
        await session.refresh(task)
        return task

    @staticmethod
    async def get_all_tasks(session: AsyncSession):
        stmt = select(db_task)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_tasks(user_id,session: AsyncSession):
        stmt = select(db_Assignment.task).where(db_Assignment.user_id==user_id)
        result = await session.execute(stmt)
        result.scalars().all()
        return result
    
    @staticmethod
    async def get_all_tasks_filtered(
        current_user,
        session: AsyncSession,
    ) -> list[db_task]:

        stmt = (
            select(db_task)
            .options(
                selectinload(db_task.assignments)
                .selectinload(db_Assignment.user)
            )
        )

        # Admin and Manager see everything
        if current_user.role in [Roles.admin, Roles.manager]:
            result = await session.execute(stmt)
            return result.scalars().all()

        # Load tasks
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        visible_tasks = []
        for task in tasks:
            is_assigned = any(assignment.user_id == current_user.id for assignment in task.assignments)
            if is_assigned:
                visible_tasks.append(task)

        return visible_tasks

    @staticmethod
    async def add_prerequisite(
        prerequisite_id: str, dependant_id: str, session: AsyncSession
    ) -> bool:
        """Returns False if either task doesn't exist, True on success."""
        stmt = (
            select(db_task)
            .options(selectinload(db_task.dependants))
            .where(db_task.id == prerequisite_id)
        )
        result = await session.execute(stmt)
        prerequisite = result.scalar_one_or_none()

        stmt = (
            select(db_task)
            .options(selectinload(db_task.prerequisites))
            .where(db_task.id == dependant_id)
        )
        result2 = await session.execute(stmt)
        dependant = result2.scalar_one_or_none()

        if prerequisite is None or dependant is None:
            return False

        prerequisite.dependants.append(dependant)
        await session.commit()
        return True
