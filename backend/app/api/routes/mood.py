import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.mood_entry import MoodEntry
from app.models.playlist import Playlist
from app.models.user import User
from app.schemas.mood import MoodAnalysisRequest, MoodAnalysisResponse
from app.services.catalog import MOOD_EMOJI
from app.services.mood_service import (
    analyze_mood,
    extract_music_preferences,
    generate_playlist_name,
)
from app.services.music_service import build_playlist

router = APIRouter()
log = logging.getLogger("moodqueue.api")


def _serialize_playlist(p: Playlist | None) -> dict | None:
    if p is None:
        return None
    return {
        "id": p.id,
        "name": p.name,
        "mood_label": p.mood_label,
        "source": p.source or ("spotify" if p.spotify_playlist_url else "catalog"),
        "spotify_playlist_url": p.spotify_playlist_url,
        "track_count": p.track_count,
        "tracks": p.tracks or [],
        "created_at": p.created_at,
    }


@router.post("/analyze", response_model=MoodAnalysisResponse)
async def analyze_user_mood(
    request: MoodAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Main endpoint: text -> mood -> playlist.
    Always returns a playlist: a real Spotify one if the account is
    connected, otherwise one built from the offline catalog.
    """
    mood_data, prefs = await asyncio.gather(
        analyze_mood(request.text),
        extract_music_preferences(request.text),
    )

    mood_entry = MoodEntry(
        user_id=current_user.id,
        raw_text=request.text,
        detected_mood=mood_data["mood"],
        confidence_score=mood_data["confidence"],
        raw_ai_response={**mood_data, "preferences": prefs},
    )
    db.add(mood_entry)
    await db.flush()

    name = await generate_playlist_name(mood_data["mood"], mood_data.get("explanation", ""))
    result = await build_playlist(current_user, mood_data, prefs, name)

    playlist = Playlist(
        user_id=current_user.id,
        mood_entry_id=mood_entry.id,
        mood_label=mood_data["mood"],
        name=name,
        spotify_playlist_id=result["spotify_playlist_id"],
        spotify_playlist_url=result["spotify_playlist_url"],
        track_ids=[t["uri"] for t in result["tracks"] if t.get("uri")],
        tracks=result["tracks"],
        source=result["source"],
        track_count=len(result["tracks"]),
    )
    db.add(playlist)
    await db.commit()  # also saves refreshed Spotify tokens on current_user
    await db.refresh(mood_entry)

    return MoodAnalysisResponse(
        mood_entry_id=mood_entry.id,
        mood=mood_data["mood"],
        emoji=MOOD_EMOJI.get(mood_data["mood"], "🎵"),
        confidence=mood_data["confidence"],
        explanation=mood_data.get("explanation", ""),
        analysis_source=mood_data.get("source", "ai"),
        playlist_generated=bool(result["tracks"]),
        playlist_id=playlist.id,
        playlist_name=name,
        playlist_url=result["spotify_playlist_url"],
        playlist_source=result["source"],
        tracks=result["tracks"],
        created_at=mood_entry.created_at,
    )


@router.get("/history")
async def get_mood_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Most recent mood entries first, each with its playlist."""
    result = await db.execute(
        select(MoodEntry)
        .options(selectinload(MoodEntry.playlist))
        .where(MoodEntry.user_id == current_user.id)
        .order_by(MoodEntry.created_at.desc())
        .limit(max(1, min(limit, 200)))
    )
    return [
        {
            "id": e.id,
            "raw_text": e.raw_text,
            "detected_mood": e.detected_mood,
            "emoji": MOOD_EMOJI.get(e.detected_mood or "", "🎵"),
            "confidence_score": e.confidence_score,
            "explanation": (e.raw_ai_response or {}).get("explanation"),
            "created_at": e.created_at,
            "playlist": _serialize_playlist(e.playlist),
        }
        for e in result.scalars().all()
    ]


@router.delete("/history/{entry_id}", status_code=204)
async def delete_mood_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes one mood entry and its playlist from the history."""
    result = await db.execute(
        select(MoodEntry)
        .options(selectinload(MoodEntry.playlist))
        .where(MoodEntry.id == entry_id, MoodEntry.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.playlist:
        await db.delete(entry.playlist)
    await db.delete(entry)
    await db.commit()
