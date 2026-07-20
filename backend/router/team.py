"""
Router layer.

Responsibility: HTTP request/response wiring only.
No business logic, no error handling - that all lives in TeamService.
"""
from fastapi import APIRouter, Depends

from dependencies.services import get_team_service
from dependencies.authorization import get_current_user,get_current_admin,get_current_manager
from models.team_models import (
    TeamCreate,
    TeamOut,
    TeamMemberCreate,
    TeamMemberOut,
    MessageCreate,
    MessageOut,
)
from schema.user import User as db_User
from services.team_service import TeamService

router_team = APIRouter()

@router_team.post("/create_team/", response_model=TeamOut)
async def create_team_route(
    data: TeamCreate,
    current_user: db_User = Depends(get_current_manager),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.create_team(data)

@router_team.post("/add_member/", response_model=TeamMemberOut)
async def add_member_route(
    data: TeamMemberCreate,
    current_user: db_User = Depends(get_current_manager),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.add_member(data.email, data.team_id)

@router_team.delete("/remove_member/{member_id}/")
async def remove_member_route(
    member_id: str,
    current_user: db_User = Depends(get_current_manager),
    team_service: TeamService = Depends(get_team_service),
):
    await team_service.remove_member(member_id, current_user)
    return {"status": "Member Removed Successfully"}

@router_team.get("/team_members/{team_id}/", response_model=list[TeamMemberOut])
async def get_team_members_route(
    team_id: str,
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.get_members(team_id, current_user)

@router_team.post("/send_message/", response_model=MessageOut)
async def send_message_route(
    data: MessageCreate,
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.send_message(data, current_user)

@router_team.get("/team_messages/{team_id}/", response_model=list[MessageOut])
async def get_team_messages_route(
    team_id: str,
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.get_messages(team_id, current_user)
