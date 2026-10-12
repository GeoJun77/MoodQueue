from app.core.time import utcnow
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.email_service import send_password_reset_email

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Creates a new user account.
    Returns a JWT token directly so the user is logged in right after registering.
    """
    # Case-insensitive checks, with a specific message for each conflict
    result = await db.execute(
        select(User).where(func.lower(User.email) == user_data.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    result = await db.execute(
        select(User).where(func.lower(User.username) == user_data.username.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken",
        )

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        # Two sign-ups with the same email/username at the same time
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )
    await db.refresh(new_user)

    token = create_access_token(user_id=new_user.id)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Logs in an existing user with JSON body.
    """
    result = await db.execute(
        select(User).where(func.lower(User.email) == user_data.email)
    )
    user = result.scalars().first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(user_id=user.id)
    return Token(access_token=token)


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2-compatible login endpoint for Swagger UI.
    """
    result = await db.execute(
        select(User).where(func.lower(User.email) == form_data.username.strip().lower())
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(user_id=user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile.
    """
    return current_user


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


def _frontend_base(request: Request) -> str:
    # FRONTEND_URL if set, otherwise the site the request came from
    if settings.FRONTEND_URL:
        return settings.FRONTEND_URL
    origin = request.headers.get("origin")
    return (origin or str(request.base_url)).rstrip("/")


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest | None = None,
    email: str | None = None,  # legacy: ?email=... query parameter
    db: AsyncSession = Depends(get_db),
):
    """
    Sends a password reset link. Always answers the same way, so nobody
    can find out which emails have an account.
    """
    address = (body.email if body else email or "").strip().lower()
    message = {"message": "If this email exists, a reset link has been sent"}
    if not address:
        return message

    result = await db.execute(select(User).where(func.lower(User.email) == address))
    user = result.scalars().first()
    if not user:
        return message

    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = utcnow() + timedelta(hours=1)
    await db.commit()

    reset_url = f"{_frontend_base(request)}/reset-password?token={reset_token}"
    await send_password_reset_email(to_email=user.email, reset_url=reset_url)
    return message


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest | None = None,
    token: str | None = None,          # legacy query parameters
    new_password: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Sets a new password using the one-time token from the email (valid 1 hour)."""
    token = body.token if body else token
    new_password = body.new_password if body else new_password
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Missing token or password")

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()

    if not user or not user.reset_token_expires or utcnow() > user.reset_token_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link",
        )

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()

    return {"message": "Password reset successfully"}


@router.delete("/me", status_code=204)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Permanently deletes the account with all its moods and playlists."""
    from sqlalchemy import delete
    from app.models.mood_entry import MoodEntry
    from app.models.playlist import Playlist

    await db.execute(delete(Playlist).where(Playlist.user_id == current_user.id))
    await db.execute(delete(MoodEntry).where(MoodEntry.user_id == current_user.id))
    await db.execute(delete(User).where(User.id == current_user.id))
    await db.commit()
