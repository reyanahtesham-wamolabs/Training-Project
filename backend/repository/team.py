from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from schema.team import Team as db_team, TeamMember as db_team_member, Message as db_message
from models.team import TeamCreate


class TeamRepo:

    @staticmethod
    async def create_team(data: TeamCreate, session: AsyncSession) -> db_team:
        team = db_team(**data.model_dump())
        session.add(team)
        await session.commit()
        await session.refresh(team)
        return team
    @staticmethod
    
    @staticmethod
    async def get_team_by_id(team_id: str, session: AsyncSession) -> db_team | None:
        return await session.get(db_team, team_id)

    @staticmethod
    async def get_all_teams(session: AsyncSession) -> list[db_team] | None:
        stmt = select(db_team)
        result = await session.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def get_team_by_project_id(project_id: str, session: AsyncSession) -> db_team | None:
        stmt = select(db_team).where(db_team.project_id == project_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_member(user_id: str, team_id: str, project_role: str, session: AsyncSession) -> db_team_member:
        member = db_team_member(user_id=user_id, team_id=team_id, project_role=project_role)
        session.add(member)
        await session.commit()
        stmt = (
            select(db_team_member)
            .where(db_team_member.id == member.id)
            .options(joinedload(db_team_member.user))
        )
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get_membership(user_id: str, team_id: str, session: AsyncSession) -> db_team_member | None:
        stmt = select(db_team_member).where(
            db_team_member.user_id == user_id, db_team_member.team_id == team_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_teams(user_id:str,session:AsyncSession):
        
        stmt = select(db_team_member.team_id).where(db_team_member.user_id==user_id)
        result = await session.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def get_member_by_id(member_id: str, session: AsyncSession) -> db_team_member | None:
        stmt = (
            select(db_team_member)
            .where(db_team_member.id == member_id)
            .options(joinedload(db_team_member.user))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_members_for_team(team_id: str, session: AsyncSession):
        from schema.user import User as db_User
        stmt = (
            select(db_team_member)
            .join(db_User, db_team_member.user_id == db_User.id)
            .where(db_team_member.team_id == team_id, db_User.active == True, db_User.soft_delete == False)
            .options(joinedload(db_team_member.user))
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_all_members_with_users(session: AsyncSession) -> list:
        """Return all TeamMember rows with the related User eagerly loaded."""
        stmt = select(db_team_member).options(joinedload(db_team_member.user))
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def remove_member(member_id: str, session: AsyncSession) -> bool:
        member = await session.get(db_team_member, member_id)
        if member is None:
            return False
        await session.delete(member)
        await session.commit()
        return True

    @staticmethod
    async def create_message(member_id: str, team_id: str, content: str, session: AsyncSession) -> db_message:
        message = db_message(member_id=member_id, team_id=team_id, content=content)
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    @staticmethod
    async def get_messages_for_team(team_id: str, session: AsyncSession):
        stmt = (
            select(db_message)
            .where(db_message.team_id == team_id)
            .order_by(db_message.sent_at.asc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def is_project_admin(user_id: str, project_id: str, session: AsyncSession) -> bool:
        from schema.enums import AssignmentRole
        from sqlalchemy import exists
        stmt = select(
            exists().where(
                db_team_member.user_id == user_id,
                db_team_member.project_role == AssignmentRole.project_admin,
                db_team_member.team_id.in_(
                    select(db_team.id).where(db_team.project_id == project_id)
                )
            )
        )
        return bool(await session.scalar(stmt))

    @staticmethod
    async def is_user_in_project_team(user_id: str, project_id: str, session: AsyncSession) -> bool:
        from sqlalchemy import exists
        stmt = select(
            exists()
            .where(db_team_member.user_id == user_id)
            .where(
                db_team_member.team_id.in_(
                    select(db_team.id).where(db_team.project_id == project_id)
                )
            )
        )
        return bool(await session.scalar(stmt))

    @staticmethod
    async def add_user_to_project_team(user_id: str, project_id: str, session: AsyncSession) -> db_team_member | None:
        import uuid
        stmt = select(db_team).where(db_team.project_id == project_id)
        res = await session.execute(stmt)
        team = res.scalar_one_or_none()
        if team is not None:
            team_member = db_team_member(
                id=str(uuid.uuid4()),
                team_id=team.id,
                user_id=user_id
            )
            session.add(team_member)
            await session.commit()
            return team_member
        return None

    @staticmethod
    async def get_member_ids_by_team(team_id: str, session: AsyncSession) -> list[str]:
        stmt = select(db_team_member.user_id).where(db_team_member.team_id == team_id)
        result = await session.execute(stmt)
        return [row[0] for row in result.all() if row[0] is not None]

    @staticmethod
    async def get_member_ids_by_project(project_id: str, session: AsyncSession) -> list[str]:
        stmt = select(db_team_member.user_id).join(db_team).where(db_team.project_id == project_id)
        result = await session.execute(stmt)
        return [row[0] for row in result.all() if row[0] is not None]