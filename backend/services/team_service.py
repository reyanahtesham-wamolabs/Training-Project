"""
Service layer.

Responsibility: business rules (membership checks, etc.) + translating
failures into HTTPExceptions. Router calls this layer only.
"""
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from repository.team import TeamRepo
from repository.project import ProjectRepo
from models.team_models import TeamCreate, MessageCreate
from schema.team import Team as db_team, TeamMember as db_team_member, Message as db_message


class TeamService:

    @staticmethod
    async def create_team(data: TeamCreate, session: AsyncSession) -> db_team:
        project = await ProjectRepo.get_project_by_id(data.project_id, session)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{data.project_id}' not found",
            )

        existing = await TeamRepo.get_team_by_project_id(data.project_id, session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This project already has a team",
            )

        try:
            return await TeamRepo.create_team(data, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create team due to a database error",
            ) from e

    @staticmethod
    async def add_member(email: str, team_id: str, session: AsyncSession) -> db_team_member:
        from repository.user_repository import get_user_by_email

        user = await get_user_by_email(email, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found",
            )

        team = await TeamRepo.get_team_by_id(team_id, session)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        existing = await TeamRepo.get_membership(user.id, team_id, session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this team",
            )

        try:
            member = await TeamRepo.add_member(user.id, team_id, session)
            from services.notification_service import NotificationService
            await NotificationService.notify_user(
                user_id=user.id,
                subject="Added to Team",
                text=f"You have been added to team '{team.name}'.",
                session=session,
            )
            return member
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this team",
            ) from e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add team member due to a database error",
            ) from e

    @staticmethod
    async def remove_member(member_id: str, current_user, session: AsyncSession) -> None:
        member = await TeamRepo.get_member_by_id(member_id, session)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")

        # Assumption: a member can only remove themselves. If you want team
        # leads/admins to be able to remove other members, extend this check.
        if member.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot remove another user from the team",
            )

        try:
            removed_user_id = member.user_id
            team_id = member.team_id
            await TeamRepo.remove_member(member_id, session)
            from services.notification_service import NotificationService
            await NotificationService.notify_user(
                user_id=removed_user_id,
                subject="Removed from Team",
                text="You have been removed from a team.",
                session=session,
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove team member due to a database error",
            ) from e

    @staticmethod
    async def get_members(team_id: str, current_user, session: AsyncSession):
        membership = await TeamRepo.get_membership(current_user.id, team_id, session)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

        try:
            return await TeamRepo.get_members_for_team(team_id, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch team members due to a database error",
            ) from e

    @staticmethod
    async def send_message(data: MessageCreate, current_user, session: AsyncSession) -> db_message:
        membership = await TeamRepo.get_membership(current_user.id, data.team_id, session)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

        try:
            message = await TeamRepo.create_message(membership.id, data.team_id, data.content, session)
            from services.notification_service import NotificationService
            await NotificationService.notify_team_members(
                team_id=data.team_id,
                subject="New Message",
                text=f"{current_user.name} sent a message in the team.",
                session=session,
                exclude_user_id=current_user.id,
                related_message_id=message.id,
            )
            return message
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message due to a database error",
            ) from e

    @staticmethod
    async def get_messages(team_id: str, current_user, session: AsyncSession):
        membership = await TeamRepo.get_membership(current_user.id, team_id, session)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

        try:
            return await TeamRepo.get_messages_for_team(team_id, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch messages due to a database error",
            ) from e