import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(user_id=new_user.id)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Logs in an existing user with JSON body.
    """
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

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
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

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


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Sends a password reset email to the user.
    Always returns success even if email doesn't exist —
    this prevents attackers from knowing which emails are registered.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Even if user doesn't exist, return success to prevent email enumeration
    if not user:
        return {"message": "If this email exists, a reset link has been sent"}

    # Generate a unique reset token valid for 1 hour
    reset_token = str(uuid.uuid4())
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

    await db.commit()

    # Send the reset email via Resend
    await send_password_reset_email(
        to_email=user.email,
        reset_token=reset_token,
    )

    return {"message": "If this email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Resets the user's password using the token from the email.
    The token is valid for 1 hour and can only be used once.
    """
    # Find user by reset token
    result = await db.execute(
        select(User).where(User.reset_token == token)
    )
    user = result.scalar_one_or_none()

    # Token not found or expired
    if not user or not user.reset_token_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if datetime.utcnow() > user.reset_token_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    # Update password and clear the token so it can't be reused
    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None

    await db.commit()

    return {"message": "Password reset successfully"}