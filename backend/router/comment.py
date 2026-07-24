from fastapi import APIRouter, Depends, status
from typing import List

from dependencies.services import get_comment_service
from dependencies.authorization import get_current_user
from schema.user import User as db_User
from models.comment import CommentCreate, CommentUpdate, CommentResponse
from services.comment import CommentService

router_comment = APIRouter()

def map_comment_to_response(db_comment) -> CommentResponse:
    replies_response = []
    if getattr(db_comment, "replies", None):
        for r in db_comment.replies:
            replies_response.append(
                CommentResponse(
                    id=r.id,
                    content=r.content,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                    user_id=r.user_id,
                    user_name=r.user.name if getattr(r, "user", None) else "",
                    task_id=r.task_id,
                    parent_comment_id=r.parent_comment_id,
                    replies=[],
                )
            )
    return CommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at,
        user_id=db_comment.user_id,
        user_name=db_comment.user.name if getattr(db_comment, "user", None) else "",
        task_id=db_comment.task_id,
        parent_comment_id=db_comment.parent_comment_id,
        replies=replies_response,
    )

@router_comment.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment_route(
    data: CommentCreate,
    current_user: db_User = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
):
    comment = await comment_service.create_comment(data, current_user)
    return map_comment_to_response(comment)

@router_comment.put("/{comment_id}", response_model=CommentResponse)
async def update_comment_route(
    comment_id: str,
    data: CommentUpdate,
    current_user: db_User = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
):
    comment = await comment_service.update_comment(comment_id, data, current_user)
    return map_comment_to_response(comment)

@router_comment.delete("/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment_route(
    comment_id: str,
    current_user: db_User = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
):
    await comment_service.delete_comment(comment_id, current_user)
    return {"status": "Comment Deleted Successfully"}

@router_comment.get("/task/{task_id}", response_model=List[CommentResponse])
async def get_task_comments_route(
    task_id: str,
    current_user: db_User = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
):
    comments = await comment_service.get_task_comments(task_id, current_user)
    return [map_comment_to_response(c) for c in comments]
