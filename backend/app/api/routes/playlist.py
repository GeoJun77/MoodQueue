import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.mood import _serialize_playlist
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_state_token, decode_state_token
from app.models.playlist import Playlist
from app.models.user import User
from app.services.spotify_service import exchange_code_for_tokens, get_spotify_auth_url

router = APIRouter()
log = logging.getLogger("moodqueue.spotify")


def _back_to_app(status: str) -> RedirectResponse:
    # FRONTEND_URL empty = the backend serves the web app itself
    return RedirectResponse(f"{settings.FRONTEND_URL}/?spotify={status}", status_code=302)


@router.get("/connect")
async def connect_spotify(current_user: User = Depends(get_current_user)):
    """Step 1 of Spotify OAuth: returns the URL the user must open."""
    if not settings.spotify_enabled:
        raise HTTPException(
            status_code=503,
            detail="Spotify is not configured on this server. Playlists use the built-in catalog.",
        )
    state = create_state_token(current_user.id, purpose="spotify")
    return {"auth_url": get_spotify_auth_url(state)}


@router.get("/callback")
async def spotify_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 2: Spotify redirects here. `state` is a signed token, so nobody
    can attach their Spotify account to another user. Then we send the
    user back to the web app.
    """
    if error or not code or not state:
        return _back_to_app("cancelled")

    user_id = decode_state_token(state, purpose="spotify")
    if not user_id:
        return _back_to_app("expired")

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        return _back_to_app("error")

    try:
        tokens = await exchange_code_for_tokens(code)
    except Exception as e:
        log.warning("Spotify token exchange failed: %s", e)
        return _back_to_app("error")

    user.spotify_access_token = tokens["access_token"]
    user.spotify_refresh_token = tokens.get("refresh_token")
    user.spotify_connected = True
    await db.commit()
    return _back_to_app("connected")


@router.post("/disconnect")
async def disconnect_spotify(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.spotify_connected = False
    current_user.spotify_access_token = None
    current_user.spotify_refresh_token = None
    await db.commit()
    return {"message": "Spotify disconnected"}


@router.get("/history")
async def get_playlist_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """All playlists generated for the current user, newest first."""
    result = await db.execute(
        select(Playlist)
        .where(Playlist.user_id == current_user.id)
        .order_by(Playlist.created_at.desc())
    )
    return [
        {**_serialize_playlist(p), "mood_entry_id": p.mood_entry_id}
        for p in result.scalars().all()
    ]
