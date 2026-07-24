from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from dependencies.services import get_team_service
from dependencies.authorization import get_current_user, get_current_admin, get_current_manager
from models.team import (
    TeamCreate,
    TeamOut,
    TeamMemberCreate,
    TeamMemberOut,
    MessageCreate,
    MessageOut,
)
from schema.user import User as db_User
from services.team import TeamService

router_team = APIRouter()


class TeamChatConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, team_id: str):
        await websocket.accept()
        if team_id not in self.active_connections:
            self.active_connections[team_id] = []
        self.active_connections[team_id].append(websocket)

    def disconnect(self, websocket: WebSocket, team_id: str):
        if team_id in self.active_connections:
            if websocket in self.active_connections[team_id]:
                self.active_connections[team_id].remove(websocket)
            if not self.active_connections[team_id]:
                del self.active_connections[team_id]

    async def broadcast(self, team_id: str, message: dict):
        if team_id in self.active_connections:
            for connection in list(self.active_connections[team_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


ws_manager = TeamChatConnectionManager()


@router_team.websocket("/ws/team_chat/{team_id}")
async def websocket_team_chat(websocket: WebSocket, team_id: str):
    await ws_manager.connect(websocket, team_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, team_id)


@router_team.post("/create_team", response_model=TeamOut)
async def create_team_route(
    data: TeamCreate,
    current_user: db_User = Depends(get_current_manager),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.create_team(data)


@router_team.post("/add_member", response_model=TeamMemberOut)
async def add_member_route(
    data: TeamMemberCreate,
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.add_member(
        email=data.email,
        team_id=data.team_id,
        project_role=data.project_role,
        current_user=current_user,
    )


@router_team.delete("/remove_member/{member_id}")
async def remove_member_route(
    member_id: str,
    current_user: db_User = Depends(get_current_manager),
    team_service: TeamService = Depends(get_team_service),
):
    await team_service.remove_member(member_id, current_user)
    return {"status": "Member Removed Successfully"}


@router_team.get("/team_members/{team_id}", response_model=list[TeamMemberOut])
async def get_team_members_route(
    team_id: str,
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.get_members(team_id, current_user)


@router_team.post("/send_message", response_model=MessageOut)
async def send_message_route(
    data: MessageCreate,
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    msg = await team_service.send_message(data, current_user)
    msg_dict = {
        "id": msg.id,
        "team_id": msg.team_id,
        "member_id": msg.member_id,
        "content": msg.content,
        "sent_at": msg.sent_at.isoformat() if hasattr(msg.sent_at, "isoformat") else str(msg.sent_at),
    }
    await ws_manager.broadcast(data.team_id, msg_dict)
    return msg


@router_team.get("/team_messages/{team_id}", response_model=list[MessageOut])
async def get_team_messages_route(
    team_id: str,
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.get_messages(team_id, current_user)


@router_team.get("/get_all_teams", response_model=list[TeamOut])
async def get_all_teams(
    current_user: db_User = Depends(get_current_manager),
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.get_all_teams()


@router_team.get("/all_members")
async def get_all_members(
    current_user: db_User = Depends(get_current_manager),
    team_service: TeamService = Depends(get_team_service),
):
    """Admin/manager: list all team members with user name and email."""
    return await team_service.get_all_members_with_users()


@router_team.get("/get_user_teams", response_model=list[TeamOut])
async def get_user_teams(
    current_user: db_User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    teams = await team_service.get_user_teams(current_user)
    return teams