from datetime import datetime

from pydantic import BaseModel
from helper_functions.validators import email_value


class TeamCreate(BaseModel):
    project_id: str
    name: str


class TeamOut(BaseModel):
    id: str
    project_id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TeamMemberCreate(BaseModel):
    email: email_value
    team_id: str


class TeamMemberOut(BaseModel):
    id: str
    user_id: str
    team_id: str
    joined_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    team_id: str
    content: str


class MessageOut(BaseModel):
    id: str
    member_id: str
    team_id: str
    content: str
    sent_at: datetime

    class Config:
        from_attributes = True