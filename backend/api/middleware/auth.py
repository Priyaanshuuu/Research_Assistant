from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt
from core.config import settings

class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: int

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)) -> str:
    """Extract and validate JWT token, return user_id"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")