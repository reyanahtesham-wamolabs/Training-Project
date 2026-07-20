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

        # Admin sees everything
        if current_user.role == Roles.admin:
            result = await session.execute(stmt)
            return result.scalars().all()

        # Load tasks
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        # Load every user's project memberships in one query
        membership_stmt = (
            select(
                db_TeamMember.user_id,
                db_Team.project_id,
            )
            .join(db_Team, db_Team.id == db_TeamMember.team_id)
        )

        membership_result = await session.execute(membership_stmt)

        user_projects: dict[str, set[str]] = {}

        for user_id, project_id in membership_result:
            user_projects.setdefault(user_id, set()).add(project_id)

        viewer_projects = user_projects.get(current_user.id, set())

        visible_tasks = []

        for task in tasks:

            assignees = [
                assignment.user
                for assignment in task.assignments
                if assignment.user
            ]

            # No assignees
            if not assignees:
                visible_tasks.append(task)
                continue

            for assignee in assignees:

                # Own task
                if assignee.id == current_user.id:
                    visible_tasks.append(task)
                    break

                if assignee.privacy_level == Levels.low:
                    visible_tasks.append(task)
                    break

                if (
                    assignee.privacy_level == Levels.medium
                    and viewer_projects &
                    user_projects.get(assignee.id, set())
                ):
                    visible_tasks.append(task)
                    break

                # High privacy -> continue checking other assignees

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
