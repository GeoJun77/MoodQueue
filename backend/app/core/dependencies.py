from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# Points Swagger to the form-compatible endpoint so the Authorize
# button works correctly in the Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/form")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency that protects routes.
    Add it to any route to require authentication:

        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            ...

    Automatically reads the Bearer token from the Authorization header,
    decodes it, and returns the matching User from the database.
    Raises 401 if the token is missing, invalid, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    # Verify the user still exists and is active in the database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user