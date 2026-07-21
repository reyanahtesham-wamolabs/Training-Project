from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    async def get_task_by_name(task_name: str, project_id: str, session: AsyncSession) -> db_task | None:
        stmt = select(db_task).where(db_task.name == task_name).where(db_task.project_id == project_id)
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
    async def get_all_tasks_filtered(current_user, session: AsyncSession) -> list[db_task]:
        """Return tasks visible to current_user according to each assignee's privacy level.

        Rules (applied per task):
        - A task with NO assignees is always visible.
        - If ANY assignee has privacy_level == low  → visible to everyone.
        - If ANY assignee has privacy_level == medium → visible to users who share
          at least one project with that assignee.
        - If ALL assignees have privacy_level == high → visible only to system admin.
        - System admin always sees everything.
        """
        from schema.assignment import Assignment as db_Assignment
        from schema.user import User as db_User
        from schema.team import Team as db_Team, TeamMember as db_TeamMember

        # System admin sees all tasks with no filtering.
        if current_user.role == Roles.admin:
            stmt = (
                select(db_task)
                .options(
                    selectinload(db_task.assignments).selectinload(db_Assignment.user)
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

        # Fetch the set of project_ids the current user belongs to via TeamMember -> Team.
        viewer_projects_stmt = (
            select(db_Team.project_id)
            .join(db_TeamMember, db_TeamMember.team_id == db_Team.id)
            .where(db_TeamMember.user_id == current_user.id)
        )
        viewer_projects_result = await session.execute(viewer_projects_stmt)
        viewer_project_ids: set[str] = {row[0] for row in viewer_projects_result.all()}

        # Load all tasks with their assignments and assignee user objects.
        stmt = (
            select(db_task)
            .options(
                selectinload(db_task.assignments).selectinload(db_Assignment.user)
            )
        )
        result = await session.execute(stmt)
        all_tasks: list[db_task] = list(result.scalars().all())

        visible_tasks: list[db_task] = []
        for task in all_tasks:
            assignees = [a.user for a in task.assignments if a.user is not None]

            # No assignees → always visible.
            if not assignees:
                visible_tasks.append(task)
                continue

            task_visible = False
            for user in assignees:
                if user.id == current_user.id:
                    # Always see your own tasks.
                    task_visible = True
                    break

                privacy = user.privacy_level
                if privacy == Levels.low:
                    # Visible to everyone.
                    task_visible = True
                    break
                elif privacy == Levels.medium:
                    # Visible if viewer shares at least one project with the assignee.
                    assignee_projects_stmt = (
                        select(db_Team.project_id)
                        .join(db_TeamMember, db_TeamMember.team_id == db_Team.id)
                        .where(db_TeamMember.user_id == user.id)
                    )
                    ap_result = await session.execute(assignee_projects_stmt)
                    assignee_project_ids = {row[0] for row in ap_result.all()}
                    if viewer_project_ids & assignee_project_ids:
                        task_visible = True
                        break
                # privacy == high → only admin can see; skip (admin handled above).

            if task_visible:
                visible_tasks.append(task)

        return visible_tasks


    @staticmethod
    async def add_prerequisite(prerequisite_id: str, dependant_id: str, session: AsyncSession) -> bool:
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