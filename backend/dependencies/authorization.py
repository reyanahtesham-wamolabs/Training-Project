from fastapi import Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from schema.user_models import User as db_User
from services.JWT_services import TokenFunctionality
from dependencies.database import get_db
from repository.user_repository import get_user_by_id
from models.user_model import UserResponse
from schema.enums import Roles
security = HTTPBearer()

async def get_current_user(
    response: Response,
    token: str = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Validates the access token and returns the current authenticated user.
    Raises HTTPException if token is invalid or login is required.
    """
    try:
        token_result = await TokenFunctionality.ensure_valid_access_token(token.credentials, session)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    if token_result["status"] == "login_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="login required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token_result["status"] == "refresh_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. refresh required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id=token_result["payload"]["sub"]

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from DB
    user = await get_user_by_id(user_id, session)

    if user is None :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_admin(
    current_user: db_User = Depends(get_current_user),
) -> db_User:
    """
    Verifies that the current user has admin privileges.
    """

    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def get_current_manager(
    current_user: db_User = Depends(get_current_user),
) -> db_User:
    """
    Verifies that the current user has admin privileges.
    """

    if not current_user.role == Roles.manager or not current_user.role==Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager privileges required",
        )
    return current_user
