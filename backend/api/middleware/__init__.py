from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from loguru import logger

from core.config import settings

bearer_scheme = HTTPBearer()


class TokenPayload(BaseModel):
    sub: str    # user_id (UUID string)
    email: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenPayload:
    """FastAPI dependency — decodes and validates the Bearer JWT on every protected route."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        email: str | None = payload.get("email")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenPayload(sub=user_id, email=email)

    except JWTError as exc:
        logger.warning("JWT validation failed: {}", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )