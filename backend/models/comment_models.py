from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from helper_functions.validators import non_empty_value

class CommentCreate(BaseModel):
    content: non_empty_value
    task_id: non_empty_value
    parent_comment_id: Optional[str] = None

class CommentUpdate(BaseModel):
    content: non_empty_value

class CommentResponse(BaseModel):
    id: str
    content: str
    created_at: datetime
    updated_at: datetime
    user_id: str
    user_name: str
    task_id: str
    parent_comment_id: Optional[str] = None
    reply: Optional["CommentResponse"] = None

    class Config:
        from_attributes = True

CommentResponse.model_rebuild()
