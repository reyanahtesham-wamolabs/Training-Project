from datetime import datetime, timedelta, UTC
import jwt
import os
from dotenv import load_dotenv
from repository.token import tokenCRUD
from repository.user import get_user_by_id
load_dotenv()

ALGORITHM=os.getenv("ALGORITHM")
SECRET_KEY=os.getenv("SECRET_KEY")
_access_exp_raw = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
_refresh_exp_raw = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

if not all([ALGORITHM, SECRET_KEY, _access_exp_raw, _refresh_exp_raw]):
    raise RuntimeError("Missing required JWT environment configuration")

ACCESS_TOKEN_EXPIRE_MINUTES = int(_access_exp_raw)
REFRESH_TOKEN_EXPIRE_DAYS = int(_refresh_exp_raw)

class  TokenFunctionality:
    @staticmethod
    def create_access_token( id: str) -> str:
        payload = {
            "sub": id,
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
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

    @staticmethod
    async def ensure_valid_access_token(access_token: str, session) -> dict:
        try:
            payload = TokenFunctionality.decode_token(access_token)
            if payload.get("type") != "access":
                return {"status": "login_required"}
            return {"status": "valid", "payload": payload}
        except jwt.ExpiredSignatureError:
            try:
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
            except jwt.InvalidTokenError:
                raise

            user_id = payload.get("sub")
            if not user_id:
                return {"status": "login_required"}
            user= await get_user_by_id(user_id,session)
            if user is None:
                return {"status": "login_required"}

            # check if a refresh token exists for this user
            try:
                has_refresh = await tokenCRUD.token_exists(user.id, session)
            except Exception:
                # on DB errors, conservatively require login
                return {"status": "login_required"}
            if has_refresh:
                return {"status":"refresh_required"}
            return{"status":"login_required"}
    @staticmethod
    async def create_refresh_token(user_id: str, session) -> str:
        exists=await tokenCRUD.get_valid_refresh_token(user_id,session)
        if exists:
            return exists.token
        expire_time=datetime.now(UTC) + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
        expire_time = expire_time.replace(tzinfo=None)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        await tokenCRUD.add_token(token, user_id, expire_time, session)
        return token
    
    @staticmethod
    async def delete_token(current_user,session):
        try:
            has_refresh = await tokenCRUD.token_exists(current_user.id, session)
        except Exception:
            return {"status": "already logged out"}
        if has_refresh:
            await tokenCRUD.delete_refresh_token(current_user.id,session)
            return "Logged out successfully"
    @staticmethod
    async def refresh_token(token,session):
        try:
            decoded_token = TokenFunctionality.decode_token(token)
        except jwt.PyJWTError:
            return {"status": "login_required"}
        user_id=decoded_token["sub"]
        flag=await tokenCRUD.token_exists(user_id,session)
        if flag:
            access_token= TokenFunctionality.create_access_token(decoded_token["sub"])
            return {"access_token": access_token,"refresh_token": token,"token_type": "bearer"}
        return {"status": "login_required"}
    