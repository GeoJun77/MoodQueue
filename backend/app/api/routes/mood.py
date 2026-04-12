from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.mood_entry import MoodEntry
from app.models.playlist import Playlist
from app.schemas.mood import MoodAnalysisRequest, MoodAnalysisResponse
from app.services.mood_service import analyze_mood, generate_playlist_name
from app.services.spotify_service import (
    get_valid_access_token,
    get_spotify_user_id,
    search_tracks_by_mood,
    create_spotify_playlist,
)

router = APIRouter()


@router.post("/analyze", response_model=MoodAnalysisResponse)
async def analyze_user_mood(
    request: MoodAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Main endpoint of MoodQueue.
    Takes the user's text, analyzes their mood with Groq LLaMA3,
    searches for matching tracks on Spotify, creates a playlist,
    and saves everything to the database.
    """

    # Step 1: Analyze mood with Groq LLaMA3
    mood_data = await analyze_mood(request.text)

    # Step 2: Save the mood entry to the database
    mood_entry = MoodEntry(
        user_id=current_user.id,
        raw_text=request.text,
        detected_mood=mood_data["mood"],
        confidence_score=mood_data["confidence"],
        raw_ai_response=mood_data,
    )
    db.add(mood_entry)
    await db.commit()
    await db.refresh(mood_entry)

    # Step 3: If user has connected Spotify, generate a playlist
    playlist_generated = False
    playlist_url = None
    playlist_name = None

    if current_user.spotify_connected:
        try:
            # Get a valid Spotify access token — auto-refreshes if expired
            access_token = await get_valid_access_token(current_user)

            # Get the real Spotify user ID.
            # This is different from our internal user ID —
            # Spotify needs its own ID to create playlists on the user's account.
            spotify_user_id = await get_spotify_user_id(access_token)

            # Use the mood label to look up our curated Spotify query dictionary.
            # Groq's raw keywords contain special characters that break Spotify search.
            keywords = mood_data["mood"]
            track_uris = await search_tracks_by_mood(access_token, keywords)

            if track_uris:
                # Generate a creative playlist name with Groq
                playlist_name = await generate_playlist_name(
                    mood=mood_data["mood"],
                    explanation=mood_data["explanation"],
                )

                # Create the actual playlist on the user's Spotify account
                spotify_data = await create_spotify_playlist(
                    access_token=access_token,
                    spotify_user_id=spotify_user_id,
                    name=playlist_name,
                    track_uris=track_uris,
                )

                # Save the playlist to our database
                playlist = Playlist(
                    user_id=current_user.id,
                    mood_entry_id=mood_entry.id,
                    mood_label=mood_data["mood"],
                    name=playlist_name,
                    spotify_playlist_id=spotify_data["spotify_playlist_id"],
                    spotify_playlist_url=spotify_data["spotify_playlist_url"],
                    track_ids=track_uris,
                    track_count=len(track_uris),
                )
                db.add(playlist)
                await db.commit()

                playlist_generated = True
                playlist_url = spotify_data["spotify_playlist_url"]

        except Exception as e:
            # Don't crash if Spotify fails — mood analysis still works.
            # The user gets their mood analyzed even without a playlist.
            print(f"Spotify playlist generation failed: {e}")

    return MoodAnalysisResponse(
        mood_entry_id=mood_entry.id,
        mood=mood_data["mood"],
        confidence=mood_data["confidence"],
        explanation=mood_data["explanation"],
        playlist_generated=playlist_generated,
        playlist_url=playlist_url,
        playlist_name=playlist_name,
        created_at=mood_entry.created_at,
    )


@router.get("/history")
async def get_mood_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the last 20 mood entries for the current user,
    ordered from most recent to oldest.
    """
    result = await db.execute(
        select(MoodEntry)
        .where(MoodEntry.user_id == current_user.id)
        .order_by(MoodEntry.created_at.desc())
        .limit(20)
    )
    entries = result.scalars().all()
    return entries