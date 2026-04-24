import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from core.config import settings
from db.database import get_db
from db.models import AuthProvider, User
from api.middleware.__init__ import TokenPayload, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OAuthUpsertRequest(BaseModel):
    email: EmailStr
    name: str | None = None
    provider: str
    provider_id: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: str | None


class MeResponse(BaseModel):
    user_id: str
    email: str

def _create_access_token(user_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _to_auth_response(user: User) -> AuthResponse:
    token = _create_access_token(str(user.id), user.email)
    return AuthResponse(
        access_token=token,
        user_id=str(user.id),
        email=user.email,
        name=user.name,
    )


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(req: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        if db.query(User).filter(User.email == req.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            id=uuid.uuid4(),
            email=req.email,
            name=req.name,
            password_hash=pwd_context.hash(req.password),
            provider=AuthProvider.EMAIL,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User registered: {}", user.email)
        return _to_auth_response(user)

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("Register error: {}", exc)
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        user = db.query(User).filter(User.email == req.email).first()
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not pwd_context.verify(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        logger.info("User logged in: {}", user.email)
        return _to_auth_response(user)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Login error: {}", exc)
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/oauth/upsert", response_model=AuthResponse)
async def oauth_upsert(
    req: OAuthUpsertRequest, db: Session = Depends(get_db)
) -> AuthResponse:
    """Called server-side by NextAuth after a successful OAuth flow.
    Upserts the user record and returns our own JWT."""
    try:
        user = db.query(User).filter(User.email == req.email).first()
        if not user:
            provider_enum = (
                AuthProvider.GOOGLE if req.provider == "google" else AuthProvider.EMAIL
            )
            user = User(
                id=uuid.uuid4(),
                email=req.email,
                name=req.name,
                provider=provider_enum,
                provider_id=req.provider_id,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("OAuth user created: {}", user.email)
        else:
            logger.info("OAuth user found: {}", user.email)

        return _to_auth_response(user)

    except Exception as exc:
        db.rollback()
        logger.error("OAuth upsert error: {}", exc)
        raise HTTPException(status_code=500, detail="OAuth upsert failed")


@router.get("/me", response_model=MeResponse)
async def me(current_user: TokenPayload = Depends(get_current_user)) -> MeResponse:
    """Protected test endpoint — verifies the JWT dependency works."""
    return MeResponse(user_id=current_user.sub, email=current_user.email)