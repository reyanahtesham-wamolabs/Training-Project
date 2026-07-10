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
            raise jwt.ExpiredSignatureError
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError

    async def create_refresh_token(email: str, session) -> str:
        expire_time=datetime.now(UTC) + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
        expire_time = expire_time.replace(tzinfo=None)
        payload = {
            "sub": str(email),
            "type": "refresh",
            "exp": expire_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        await tokenCRUD.add_token(token, email, expire_time, session)
        return token
    
