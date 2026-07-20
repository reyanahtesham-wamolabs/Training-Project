from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schema.team import Team as db_team, TeamMember as db_team_member, Message as db_message
from models.team_models import TeamCreate


class TeamRepo:

    @staticmethod
    async def create_team(data: TeamCreate, session: AsyncSession) -> db_team:
        team = db_team(**data.model_dump())
        session.add(team)
        await session.commit()
        await session.refresh(team)
        return team

    @staticmethod
    async def get_team_by_id(team_id: str, session: AsyncSession) -> db_team | None:
        return await session.get(db_team, team_id)

    @staticmethod
    async def get_team_by_project_id(project_id: str, session: AsyncSession) -> db_team | None:
        stmt = select(db_team).where(db_team.project_id == project_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_member(user_id: str, team_id: str, session: AsyncSession) -> db_team_member:
        member = db_team_member(user_id=user_id, team_id=team_id)
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member

    @staticmethod
    async def get_membership(user_id: str, team_id: str, session: AsyncSession) -> db_team_member | None:
        stmt = select(db_team_member).where(
            db_team_member.user_id == user_id, db_team_member.team_id == team_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_member_by_id(member_id: str, session: AsyncSession) -> db_team_member | None:
        return await session.get(db_team_member, member_id)

    @staticmethod
    async def get_members_for_team(team_id: str, session: AsyncSession):
        stmt = select(db_team_member).where(db_team_member.team_id == team_id)
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