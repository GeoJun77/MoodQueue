"""
Spotify integration (optional).

Only used when SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET are set AND the
user connected their account. Every function here may fail (Spotify
policies change often): callers catch errors and fall back to the
built-in catalog.
"""
import asyncio
import base64
import logging
import random
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.services.catalog import make_track

log = logging.getLogger("moodqueue.spotify")

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"
SPOTIFY_SCOPES = "playlist-modify-public playlist-modify-private user-read-private user-read-email"
TIMEOUT = httpx.Timeout(15.0)
MAX_TRACKS = 50


def get_spotify_auth_url(state: str) -> str:
    """Spotify OAuth2 authorization URL. `state` is a signed, short-lived token."""
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "state": state,
        "show_dialog": "true",
    }
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"


def _basic_auth() -> str:
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    return base64.b64encode(credentials.encode()).decode()


async def _token_request(data: dict) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            headers={
                "Authorization": f"Basic {_basic_auth()}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=data,
        )
        response.raise_for_status()
        return response.json()


async def exchange_code_for_tokens(code: str) -> dict:
    return await _token_request({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
    })


async def refresh_spotify_token(refresh_token: str) -> dict:
    """Returns the token payload (may contain a rotated refresh_token)."""
    return await _token_request({"grant_type": "refresh_token", "refresh_token": refresh_token})


async def get_valid_access_token(user) -> str:
    """
    Returns a working access token, refreshing it if needed.
    Updates the user object in place (caller commits).
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{SPOTIFY_API_URL}/me",
                headers={"Authorization": f"Bearer {user.spotify_access_token}"},
            )
            if response.status_code == 200:
                return user.spotify_access_token
    except httpx.HTTPError:
        pass

    data = await refresh_spotify_token(user.spotify_refresh_token)
    user.spotify_access_token = data["access_token"]
    if data.get("refresh_token"):
        user.spotify_refresh_token = data["refresh_token"]
    return user.spotify_access_token


async def get_spotify_user_id(access_token: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"{SPOTIFY_API_URL}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()["id"]


def _to_track(item: dict) -> dict | None:
    if not item or not item.get("uri"):
        return None
    artists = ", ".join(a.get("name", "") for a in item.get("artists", []) if a.get("name"))
    url = (item.get("external_urls") or {}).get("spotify")
    return make_track(item.get("name", "Unknown"), artists or "Unknown", uri=item["uri"], url=url)


async def _search(client: httpx.AsyncClient, access_token: str, query: str, limit: int) -> list[dict]:
    """One Spotify track search. Never raises: returns [] on any error."""
    try:
        response = await client.get(
            f"{SPOTIFY_API_URL}/search",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"q": query.replace(",", " ").strip(), "type": "track", "limit": limit},
        )
        if response.status_code != 200:
            log.info("Spotify search %r -> HTTP %s", query, response.status_code)
            return []
        items = response.json().get("tracks", {}).get("items", [])
        return [t for t in (_to_track(i) for i in items) if t]
    except Exception as e:
        log.info("Spotify search %r failed: %s", query, e)
        return []


def _merge(results: list[list[dict]], seen: set[str]) -> list[dict]:
    out = []
    for tracks in results:
        for track in tracks:
            if track["uri"] not in seen:
                seen.add(track["uri"])
                out.append(track)
    return out


async def search_tracks_by_mood(
    access_token: str,
    mood_data: dict,
    explicit_artists: list[str] | None = None,
    explicit_genres: list[str] | None = None,
) -> list[dict]:
    """
    3-layer smart search:
      1. Explicit artists  -> only their tracks (+ explicit genres), shuffled
      2. Explicit genres   -> genre tracks first, mood tracks fill the rest
      3. Otherwise         -> AI mood queries + genres, shuffled
    """
    explicit_artists = explicit_artists or []
    explicit_genres = explicit_genres or []
    mood = mood_data.get("mood", "happy")
    ai_genres = mood_data.get("genres") or ["pop", "indie"]
    queries = mood_data.get("search_queries") or [mood]

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        if explicit_artists:
            tasks = []
            for artist in explicit_artists:
                tasks.append(_search(client, access_token, f"artist:{artist}", 10))
                tasks.append(_search(client, access_token, artist, 10))
            tasks += [_search(client, access_token, f"{g} {mood}", 10) for g in explicit_genres]
            tracks = _merge(await asyncio.gather(*tasks), set())
            random.shuffle(tracks)
            return tracks[:MAX_TRACKS]

        if explicit_genres:
            genre_res = await asyncio.gather(
                *[_search(client, access_token, f"{g} {mood}", 10) for g in explicit_genres]
            )
            mood_res = await asyncio.gather(*[_search(client, access_token, q, 6) for q in queries])
            seen: set[str] = set()
            tracks = _merge(genre_res, seen)
            filler = _merge(mood_res, seen)
            random.shuffle(filler)
            return (tracks + filler)[:MAX_TRACKS]

        all_queries = list(queries) + [f"{mood} {g}" for g in ai_genres[:4]]
        tracks = _merge(
            await asyncio.gather(*[_search(client, access_token, q, 6) for q in all_queries]),
            set(),
        )
        random.shuffle(tracks)
        return tracks[:MAX_TRACKS]


async def create_spotify_playlist(
    access_token: str,
    spotify_user_id: str,
    name: str,
    track_uris: list[str],
) -> dict:
    """Creates a private playlist and adds up to 50 tracks."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        create = await client.post(
            f"{SPOTIFY_API_URL}/me/playlists",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": name,
                "description": "Generated by MoodQueue 🎵",
                "public": False,
                "collaborative": False,
            },
        )
        create.raise_for_status()
        playlist = create.json()

        if track_uris:
            await asyncio.sleep(0.5)
            add = await client.post(
                f"{SPOTIFY_API_URL}/playlists/{playlist['id']}/items",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"uris": track_uris[:MAX_TRACKS]},
            )
            if add.status_code == 404:  # older endpoint name, just in case
                add = await client.post(
                    f"{SPOTIFY_API_URL}/playlists/{playlist['id']}/tracks",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"uris": track_uris[:MAX_TRACKS]},
                )
            if add.status_code >= 300:
                log.warning("Adding tracks failed: %s %s", add.status_code, add.text[:200])

        return {
            "spotify_playlist_id": playlist["id"],
            "spotify_playlist_url": playlist["external_urls"]["spotify"],
        }
