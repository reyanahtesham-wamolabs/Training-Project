from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from dependencies.database import get_db
from dependencies.authorization import get_current_user
from schema.user import User as db_User
from models.comment_models import CommentCreate, CommentUpdate, CommentResponse
from services.comment_services import CommentService

router_comment = APIRouter()

def map_comment_to_response(db_comment) -> CommentResponse:
    reply_response = None
    if db_comment.reply:
        reply_response = CommentResponse(
            id=db_comment.reply.id,
            content=db_comment.reply.content,
            created_at=db_comment.reply.created_at,
            updated_at=db_comment.reply.updated_at,
            user_id=db_comment.reply.user_id,
            user_name=db_comment.reply.user.name if db_comment.reply.user else "",
            task_id=db_comment.reply.task_id,
            parent_comment_id=db_comment.reply.parent_comment_id,
            reply=None,
        )
    return CommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at,
        user_id=db_comment.user_id,
        user_name=db_comment.user.name if db_comment.user else "",
        task_id=db_comment.task_id,
        parent_comment_id=db_comment.parent_comment_id,
        reply=reply_response,
    )

@router_comment.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment_route(
    data: CommentCreate,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    comment = await CommentService.create_comment(data, current_user, session)
    return map_comment_to_response(comment)

@router_comment.put("/{comment_id}/", response_model=CommentResponse)
async def update_comment_route(
    comment_id: str,
    data: CommentUpdate,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    comment = await CommentService.update_comment(comment_id, data, current_user, session)
    return map_comment_to_response(comment)

@router_comment.delete("/{comment_id}/", status_code=status.HTTP_200_OK)
async def delete_comment_route(
    comment_id: str,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await CommentService.delete_comment(comment_id, current_user, session)
    return {"status": "Comment Deleted Successfully"}

@router_comment.get("/task/{task_id}/", response_model=List[CommentResponse])
async def get_task_comments_route(
    task_id: str,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    comments = await CommentService.get_task_comments(task_id, current_user, session)
    return [map_comment_to_response(c) for c in comments]
