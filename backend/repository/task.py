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
        stmt = (
            select(db_task)
            .options(
                selectinload(db_task.prerequisites),
                selectinload(db_task.dependants),
                selectinload(db_task.assignments).selectinload(db_Assignment.user),
            )
            .where(db_task.id == task_id)
        )
        result=await session.execute(stmt)
        task = result.scalar_one_or_none()
        if task and hasattr(task, 'prerequisites') and task.prerequisites:
            task.prerequisites = [p for p in task.prerequisites if not getattr(p, 'soft_delete', False)]
        return task

    @staticmethod
    async def delete_task(task_id: str, session: AsyncSession) -> bool:
        from schema.task import association_table
        from sqlalchemy import delete, or_

        task = await session.get(db_task, task_id)
        if task is None:
            return False

        task.soft_delete = True
        await session.execute(
            delete(association_table).where(
                or_(
                    association_table.c.prerequisite_task_id == task_id,
                    association_table.c.dependant_task_id == task_id
                )
            )
        )
        await session.commit()
        return True

    @staticmethod
    async def restore_task(task_id: str, session: AsyncSession) -> bool:
        task = await session.get(db_task, task_id)
        if task is None:
            return False

        task.soft_delete = False
        await session.commit()
        return True

    @staticmethod
    async def hard_delete_task(task_id: str, session: AsyncSession) -> bool:
        from schema.task import association_table
        from schema.assignment import Assignment as db_Assignment
        from schema.comment import Comment as db_Comment
        from sqlalchemy import delete, or_

        task = await session.get(db_task, task_id)
        if task is None:
            return False

        await session.execute(
            delete(association_table).where(
                or_(
                    association_table.c.prerequisite_task_id == task_id,
                    association_table.c.dependant_task_id == task_id
                )
            )
        )
        await session.execute(delete(db_Assignment).where(db_Assignment.task_id == task_id))
        await session.execute(delete(db_Comment).where(db_Comment.task_id == task_id))

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

        # If status is updated away from archived or soft_delete is explicitly False, clear soft_delete
        if getattr(data, "soft_delete", None) is False:
            task.soft_delete = False
        elif getattr(data, "status", None) and str(data.status).lower() != "archived":
            task.soft_delete = False

        await session.commit()
        await session.refresh(task)
        return task

    @staticmethod
    async def get_all_tasks(session: AsyncSession):
        stmt = select(db_task).where(db_task.soft_delete == False)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_tasks(user_id, session: AsyncSession):
        stmt = select(db_Assignment.task).join(db_task).where(db_Assignment.user_id == user_id, db_task.soft_delete == False)
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
                selectinload(db_task.prerequisites),
                selectinload(db_task.assignments)
                .selectinload(db_Assignment.user)
            )
        )

        # Admin and Manager see everything
        if current_user.role in [Roles.admin, Roles.manager]:
            result = await session.execute(stmt)
            all_t = list(result.scalars().all())
            for t in all_t:
                if hasattr(t, 'prerequisites') and t.prerequisites:
                    t.prerequisites = [p for p in t.prerequisites if not getattr(p, 'soft_delete', False)]
            return all_t

        # Determine which projects the user is "assigned to"
        # 1. Projects where user is in the team
        team_stmt = select(db_Team.project_id).join(db_TeamMember).where(db_TeamMember.user_id == current_user.id)
        team_res = await session.execute(team_stmt)
        project_ids_from_teams = set(team_res.scalars().all())

        # 2. Projects where user has a task assignment
        assignment_stmt = select(db_task.project_id).join(db_Assignment).where(db_Assignment.user_id == current_user.id)
        assignment_res = await session.execute(assignment_stmt)
        project_ids_from_assignments = set(assignment_res.scalars().all())

        assigned_project_ids = project_ids_from_teams | project_ids_from_assignments

        # Load tasks
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        visible_tasks = []
        for task in tasks:
            # 1. User is directly assigned to the task
            is_assigned = any(assignment.user_id == current_user.id for assignment in task.assignments)
            if is_assigned:
                visible_tasks.append(task)
                continue

            # 2. Task is in a project the user is assigned to
            if task.project_id in assigned_project_ids:
                if not task.assignments:
                    # Task has no assignees, so it's visible to project members
                    visible_tasks.append(task)
                    continue

                # Check if any assignee has high privacy
                has_high_privacy = False
                for assignment in task.assignments:
                    if assignment.user:
                        priv = getattr(assignment.user.privacy_level, 'value', assignment.user.privacy_level)
                        if priv == 'high' or priv == Levels.high:
                            has_high_privacy = True
                            break
                            
                if not has_high_privacy:
                    visible_tasks.append(task)

        for t in visible_tasks:
            if hasattr(t, 'prerequisites') and t.prerequisites:
                t.prerequisites = [p for p in t.prerequisites if not getattr(p, 'soft_delete', False)]

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

    @staticmethod
    async def get_assignee_ids_by_task(task_id: str, session: AsyncSession) -> list[str]:
        stmt = select(db_Assignment.user_id).where(db_Assignment.task_id == task_id)
        result = await session.execute(stmt)
        return [row[0] for row in result.all() if row[0] is not None]

    @staticmethod
    async def shift_dependants_to_planned(task: db_task, session: AsyncSession):
        from schema.enums import ProjectStatus
        planned_val = ProjectStatus.planned if hasattr(ProjectStatus, 'planned') else 'planned'
        changed = False
        for dep in task.dependants:
            dep_status = str(getattr(dep.status, 'value', dep.status))
            if dep_status != 'planned':
                dep.status = planned_val
                session.add(dep)
                changed = True
        if changed:
            await session.commit()
            await session.refresh(task)
