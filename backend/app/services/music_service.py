"""
Builds the playlist for a mood: Spotify when possible, built-in catalog otherwise.
"""
import logging
import random

from app.core.config import settings
from app.services.catalog import CATALOG, make_track
from app.services.local_mood import GENRE_MOOD, normalize
from app.services import spotify_service

log = logging.getLogger("moodqueue.music")

# When a mood has few matches, borrow from close moods
NEIGHBOURS = {
    "happy": ["party", "hopeful"], "sad": ["melancholic", "lonely"],
    "angry": ["motivated", "energetic"], "calm": ["focused", "anxious"],
    "energetic": ["party", "motivated"], "nostalgic": ["happy", "melancholic"],
    "romantic": ["calm", "happy"], "focused": ["calm"], "anxious": ["calm", "hopeful"],
    "melancholic": ["sad", "lonely"], "spiritual": ["hopeful", "calm"],
    "party": ["energetic", "happy"], "motivated": ["energetic", "angry"],
    "lonely": ["sad", "melancholic"], "hopeful": ["happy", "spiritual"],
    "homesick": ["nostalgic", "party"],
}

PLAYLIST_SIZE = 15


def build_catalog_playlist(mood: str, artists: list[str], genres: list[str]) -> list[dict]:
    """Offline playlist from the built-in catalog. Always returns tracks."""
    mood = mood if mood in CATALOG else "calm"
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []

    def add(items):
        for item in items:
            if item not in seen and len(out) < PLAYLIST_SIZE:
                seen.add(item)
                out.append(item)

    # 1. Tracks by artists the user named (if we know them)
    wanted = [normalize(a) for a in artists]
    by_artist = [
        t for tracks in CATALOG.values() for t in tracks
        if any(w and w in normalize(t[1]) for w in wanted)
    ]
    add(by_artist)

    # 2. The mood itself, shuffled so each playlist feels different
    main = CATALOG[mood][:]
    random.shuffle(main)
    add(main[:10])

    # 3. Genres the user named
    for g in genres:
        g_mood = GENRE_MOOD.get(normalize(g))
        if g_mood and g_mood != mood:
            extra = CATALOG[g_mood][:]
            random.shuffle(extra)
            add(extra[:4])

    # 4. Fill with the rest of the mood, then close moods
    add(main)
    for n in NEIGHBOURS.get(mood, []):
        extra = CATALOG[n][:]
        random.shuffle(extra)
        add(extra)

    return [make_track(title, artist) for title, artist in out]


async def build_playlist(user, mood_data: dict, prefs: dict, name: str) -> dict:
    """
    Returns {"tracks", "source", "spotify_playlist_id", "spotify_playlist_url"}.
    Tries Spotify if the user connected it; any failure -> catalog.
    """
    artists, genres = prefs.get("artists", []), prefs.get("genres", [])

    if settings.spotify_enabled and user.spotify_connected and user.spotify_refresh_token:
        try:
            token = await spotify_service.get_valid_access_token(user)
            tracks = await spotify_service.search_tracks_by_mood(token, mood_data, artists, genres)
            if tracks:
                spotify_user_id = await spotify_service.get_spotify_user_id(token)
                created = await spotify_service.create_spotify_playlist(
                    token, spotify_user_id, name, [t["uri"] for t in tracks]
                )
                return {"tracks": tracks, "source": "spotify", **created}
        except Exception as e:
            log.warning("Spotify playlist failed, using built-in catalog: %s", e)

    return {
        "tracks": build_catalog_playlist(mood_data["mood"], artists, genres),
        "source": "catalog",
        "spotify_playlist_id": None,
        "spotify_playlist_url": None,
    }
