from datetime import datetime

from pydantic import BaseModel,ConfigDict
from helper_functions.validators import email_value


class TeamCreate(BaseModel):
    project_id: str
    name: str


class TeamOut(BaseModel):
    id: str
    project_id: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamMemberCreate(BaseModel):
    email: email_value
    team_id: str
    project_role: str = "project_member"


class TeamMemberOut(BaseModel):
    id: str
    user_id: str
    team_id: str
    joined_at: datetime
    name: str | None = None
    email: str | None = None
    project_role: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    team_id: str
    content: str


class MessageOut(BaseModel):
    id: str
    member_id: str
    team_id: str
    content: str
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)
