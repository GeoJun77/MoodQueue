from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.playlist import Playlist
from app.services.spotify_service import (
    get_spotify_auth_url,
    exchange_code_for_tokens,
    create_spotify_playlist,
    search_tracks_by_mood,
)

router = APIRouter()


@router.get("/connect")
async def connect_spotify(current_user: User = Depends(get_current_user)):
    """
    Step 1 of Spotify OAuth2 flow.
    Returns the Spotify authorization URL the user must visit
    to grant MoodQueue access to their account.
    """
    auth_url = get_spotify_auth_url(user_id=current_user.id)
    return {"auth_url": auth_url}


@router.get("/callback")
async def spotify_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 2 of Spotify OAuth2 flow.
    Spotify redirects here after the user grants access.
    "code" is the authorization code we exchange for tokens.
    "state" is the user_id we passed earlier — Spotify sends it back
    so we know which user just connected their account.
    """

    # Exchange the authorization code for real access + refresh tokens
    tokens = await exchange_code_for_tokens(code)

    # Retrieve the user from the database using the state (user_id)
    result = await db.execute(select(User).where(User.id == state))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Save Spotify tokens and mark the account as connected
    user.spotify_access_token = tokens["access_token"]
    user.spotify_refresh_token = tokens["refresh_token"]
    user.spotify_connected = True

    await db.commit()

    # In production this would redirect to the mobile app via deep link
    return {"message": "Spotify connected successfully!", "user_id": state}


@router.get("/history")
async def get_playlist_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all playlists previously generated for the current user,
    ordered from most recent to oldest.
    """
    result = await db.execute(
        select(Playlist)
        .where(Playlist.user_id == current_user.id)
        .order_by(Playlist.created_at.desc())
    )
    playlists = result.scalars().all()
    return playlists