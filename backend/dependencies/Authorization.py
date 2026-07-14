from fastapi import Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from schema.user_models import User as db_User
from services.JWT_services import TokenFunctionality
from dependencies.database import get_db
from repository.user_repository import get_user_by_email
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
    If token is expired, attempts to refresh using stored refresh token.
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
            detail="Token expired. login required",
            headers={"WWW-Authenticate": "Bearer"},
        )



    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from DB
    user = await get_user_by_email(user_email, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_admin(
    current_user: db_User = Depends(get_current_user),
) -> db_User:
    """
    Verifies that the current user has admin privileges.
    Use this as a dependency when admin-only access is required.
    """

    if current_user.role != Roles.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
