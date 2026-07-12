from datetime import datetime, timedelta, UTC
import jwt
import os
from dotenv import load_dotenv
from repository.token import tokenCRUD 
load_dotenv()

ALGORITHM=os.getenv("ALGORITHM")
SECRET_KEY=os.getenv("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

class TokenFunctionality:
    def create_access_token( email: str) -> str:
        payload = {
            "sub": email,
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(token: str):
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise

    async def ensure_valid_access_token(access_token: str, session) -> dict:
        """
        - {"status": "valid", "payload": <payload>} when access token is valid
        - {"status": "refreshed", "access_token": <new_token>} when a new access token was issued
        - {"status": "login_required"} when token expired and no valid refresh token exists
        """
        try:
            payload = TokenFunctionality.decode_token(access_token)
            return {"status": "valid", "payload": payload}
        except jwt.ExpiredSignatureError:
            # decode without verifying expiration to extract subject
            try:
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
            except jwt.InvalidTokenError:
                # signature invalid
                raise

            user_email = payload.get("sub")
            if not user_email:
                return {"status": "login_required"}

            # check if a refresh token exists for this user
            try:
                has_refresh = await tokenCRUD.token_exists(user_email, session)
            except Exception:
                # on DB errors, conservatively require login
                return {"status": "login_required"}

            if has_refresh:
                # issue a new access token
                new_access = TokenFunctionality.create_access_token(user_email)
                return {"status": "refreshed", "access_token": new_access}
            else:
                return {"status": "login_required"}

    async def create_refresh_token(email: str, session) -> str:
        expire_time=datetime.now(UTC) + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
        expire_time = expire_time.replace(tzinfo=None)
        payload = {
            "sub": str(email),
            "type": "refresh",
            "exp": expire_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        flag = await tokenCRUD.token_exists(email, session)
        if not flag:
            await tokenCRUD.add_token(token, email, expire_time, session)
        return token