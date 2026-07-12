from fastapi import Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema.user_models import User as db_User
from services.JWT_services import TokenFunctionality
from dependencies.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
    response: Response | None = None,
) -> db_User:
    """
    Validates the access token and returns the current authenticated user.
    If token is expired, attempts to refresh using stored refresh token.
    Raises HTTPException if token is invalid or login is requi red.
    """
    try:
        token_result = await TokenFunctionality.ensure_valid_access_token(token, session)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    if token_result["status"] == "login_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please login again",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract email from payload
    if token_result["status"] == "refreshed":
        payload = TokenFunctionality.decode_token(token_result["access_token"])
        user_email = payload.get("sub")
        if response is not None:
            response.headers["X-Access-Token"] = token_result["access_token"]
    else:  # "valid"
        user_email = token_result["payload"].get("sub")

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from DB
    stmt = select(db_User).where(db_User.email == user_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

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
    from schema.enums import Roles

    if current_user.role != Roles.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
