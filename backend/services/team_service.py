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
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def get_all_teams(self) -> list[db_team]|None:
        teams=await TeamRepo.get_all_teams(self.session)
        return teams

    async def get_all_members_with_users(self) -> list:
        """Return all team members with user name and email for admin views."""
        members = await TeamRepo.get_all_members_with_users(self.session)
        result = []
        for m in members:
            result.append({
                "id": m.id,
                "user_id": m.user_id,
                "team_id": m.team_id,
                "joined_at": m.joined_at.isoformat(),
                "name": m.user.name if m.user else None,
                "email": m.user.email if m.user else None,
            })
        return result

    async def get_user_teams(self, current_user) -> list[db_team]:
        team_ids = await TeamRepo.get_user_teams(current_user.id, self.session)
        teams = []
        for team_id in team_ids:
            team = await TeamRepo.get_team_by_id(team_id, self.session)
            if team is not None:
                teams.append(team)
        return teams

    async def create_team(self, data: TeamCreate) -> db_team:
        project = await ProjectRepo.get_project_by_id(data.project_id, self.session)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{data.project_id}' not found",
            )

        existing = await TeamRepo.get_team_by_project_id(data.project_id, self.session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This project already has a team",
            )

        try:
            return await TeamRepo.create_team(data, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create team due to a database error",
            ) from e

    async def add_member(self, email: str, team_id: str) -> db_team_member:
        from repository.user_repository import get_user_by_email

        user = await get_user_by_email(email, self.session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found",
            )

        team = await TeamRepo.get_team_by_id(team_id, self.session)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        existing = await TeamRepo.get_membership(user.id, team_id, self.session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this team",
            )

        try:
            member = await TeamRepo.add_member(user.id, team_id, self.session)
            from services.notification_service import NotificationService
            await NotificationService.notify_user(
                user_id=user.id,
                subject="Added to Team",
                text=f"You have been added to team '{team.name}'.",
                session=self.session,
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

    async def remove_member(self, member_id: str, current_user) -> None:
        member = await TeamRepo.get_member_by_id(member_id, self.session)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found")

        if member.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot remove another user from the team",
            )

        try:
            removed_user_id = member.user_id
            await TeamRepo.remove_member(member_id, self.session)
            from services.notification_service import NotificationService
            await NotificationService.notify_user(
                user_id=removed_user_id,
                subject="Removed from Team",
                text="You have been removed from a team.",
                session=self.session,
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove team member due to a database error",
            ) from e

    async def get_members(self, team_id: str, current_user):
        membership = await TeamRepo.get_membership(current_user.id, team_id, self.session)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

        try:
            return await TeamRepo.get_members_for_team(team_id, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch team members due to a database error",
            ) from e

    async def send_message(self, data: MessageCreate, current_user) -> db_message:
        membership = await TeamRepo.get_membership(current_user.id, data.team_id, self.session)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

        try:
            message = await TeamRepo.create_message(membership.id, data.team_id, data.content, self.session)
            from services.notification_service import NotificationService
            await NotificationService.notify_team_members(
                team_id=data.team_id,
                subject="New Message",
                text=f"{current_user.name} sent a message in the team.",
                session=self.session,
                exclude_user_id=current_user.id,
                related_message_id=message.id,
            )
            return message
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message due to a database error",
            ) from e

    async def get_messages(self, team_id: str, current_user):
        membership = await TeamRepo.get_membership(current_user.id, team_id, self.session)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

        try:
            return await TeamRepo.get_messages_for_team(team_id, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch messages due to a database error",
            ) from e