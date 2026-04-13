import httpx
import base64
import asyncio
import random
from app.core.config import settings

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

SPOTIFY_SCOPES = "playlist-modify-public playlist-modify-private user-read-private user-read-email"


def get_spotify_auth_url(user_id: str) -> str:
    """
    Builds the Spotify OAuth2 authorization URL.
    show_dialog=true forces Spotify to show the permission screen again
    to ensure new scopes are properly granted.
    """
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "state": user_id,
        "show_dialog": "true",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{SPOTIFY_AUTH_URL}?{query}"


async def exchange_code_for_tokens(code: str) -> dict:
    """
    Exchanges the authorization code for access and refresh tokens.
    """
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            },
        )
        response.raise_for_status()
        return response.json()


async def refresh_spotify_token(refresh_token: str) -> str:
    """
    Uses the refresh token to get a new access token
    without asking the user to log in again.
    """
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]


async def get_valid_access_token(user) -> str:
    """
    Returns a valid Spotify access token.
    Automatically refreshes if expired.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SPOTIFY_API_URL}/me",
                headers={"Authorization": f"Bearer {user.spotify_access_token}"},
            )
            if response.status_code == 200:
                return user.spotify_access_token
    except Exception:
        pass

    return await refresh_spotify_token(user.spotify_refresh_token)


async def get_spotify_user_id(access_token: str) -> str:
    """
    Fetches the Spotify user ID for the authenticated user.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SPOTIFY_API_URL}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()["id"]


async def search_single_query(
    client: httpx.AsyncClient,
    access_token: str,
    query: str,
    limit: int = 8,
) -> list[str]:
    """
    Performs a single Spotify search and returns track URIs.
    """
    try:
        clean_query = query.replace(",", "").replace("-", " ").strip()

        response = await client.get(
            f"{SPOTIFY_API_URL}/search",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "q": clean_query,
                "type": "track",
                "limit": limit,
            },
        )

        if response.status_code != 200:
            print(f"DEBUG search error for '{clean_query}': {response.status_code}")
            return []

        data = response.json()
        tracks = data.get("tracks", {}).get("items", [])
        return [track["uri"] for track in tracks if track.get("uri")]

    except Exception as e:
        print(f"DEBUG search exception for '{query}': {e}")
        return []


async def search_tracks_by_artist(
    client: httpx.AsyncClient,
    access_token: str,
    artist: str,
    limit: int = 10,
) -> list[str]:
    """
    Searches for tracks by a specific artist using two strategies:
    1. artist: prefix — finds official tracks by this artist
    2. Plain name search — finds features, remixes, and collaborations
    Both are merged and deduplicated for maximum coverage.
    """
    try:
        # Strategy 1: strict artist search
        response1 = await client.get(
            f"{SPOTIFY_API_URL}/search",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "q": f"artist:{artist}",
                "type": "track",
                "limit": limit,
            },
        )

        # Strategy 2: plain name search — catches features and remixes
        response2 = await client.get(
            f"{SPOTIFY_API_URL}/search",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "q": artist,
                "type": "track",
                "limit": limit,
            },
        )

        uris = []
        seen = set()

        for response in [response1, response2]:
            if response.status_code == 200:
                tracks = response.json().get("tracks", {}).get("items", [])
                for track in tracks:
                    uri = track.get("uri")
                    if uri and uri not in seen:
                        seen.add(uri)
                        uris.append(uri)

        print(f"DEBUG artist '{artist}': found {len(uris)} tracks")
        return uris

    except Exception as e:
        print(f"DEBUG artist search error for '{artist}': {e}")
        return []


async def search_tracks_by_genre(
    client: httpx.AsyncClient,
    access_token: str,
    genre: str,
    mood: str,
    limit: int = 8,
) -> list[str]:
    """
    Searches for tracks in a specific genre.
    Combines genre with mood for more contextual results.
    """
    try:
        query = f"{genre} {mood}"
        response = await client.get(
            f"{SPOTIFY_API_URL}/search",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "q": query,
                "type": "track",
                "limit": limit,
            },
        )
        if response.status_code != 200:
            return []

        data = response.json()
        tracks = data.get("tracks", {}).get("items", [])
        return [track["uri"] for track in tracks if track.get("uri")]

    except Exception as e:
        print(f"DEBUG genre search error for '{genre}': {e}")
        return []


async def search_tracks_by_mood(
    access_token: str,
    mood_data: dict,
    explicit_artists: list[str] = [],
    explicit_genres: list[str] = [],
) -> list[str]:
    """
    3-layer smart search system:

    CASE 1 — Explicit artists detected:
        → ONLY tracks from those artists, no mood filler at all
        → Tracks shuffled so artists are mixed together
        → e.g. "I want only Oklou, Addison Rae and Bad Bunny"

    CASE 2 — Explicit genres detected (no artists):
        → Genre tracks first, mood tracks fill the rest
        → e.g. "I'm sad but I want electro and house"

    CASE 3 — No explicit preferences:
        → Pure AI mood queries + genre queries, all shuffled
        → e.g. "I feel nostalgic tonight"
    """
    mood = mood_data.get("mood", "happy")
    ai_genres = mood_data.get("genres", ["pop", "indie"])
    search_queries = mood_data.get("search_queries", [mood])

    async with httpx.AsyncClient() as client:

        # CASE 1: Explicit artists → ONLY their tracks
        if explicit_artists:
            print(f"DEBUG artist-only mode: {explicit_artists}")
            artist_tasks = [
                search_tracks_by_artist(client, access_token, artist, limit=10)
                for artist in explicit_artists
            ]
            # Also include explicit genres if mentioned alongside artists
            genre_tasks = [
                search_tracks_by_genre(client, access_token, genre, mood, limit=10)
                for genre in explicit_genres
            ]

            all_results = await asyncio.gather(*artist_tasks, *genre_tasks)

            seen = set()
            final_uris = []
            for track_list in all_results:
                for uri in track_list:
                    if uri not in seen:
                        seen.add(uri)
                        final_uris.append(uri)

            # Shuffle so tracks from different artists are interleaved
            random.shuffle(final_uris)
            print(f"DEBUG artist-only: {len(final_uris)} tracks")
            return final_uris[:50]

        # CASE 2: Explicit genres, no artists → genre first then mood
        if explicit_genres:
            print(f"DEBUG genre-priority mode: {explicit_genres}")
            genre_tasks = [
                search_tracks_by_genre(client, access_token, genre, mood, limit=10)
                for genre in explicit_genres
            ]
            mood_tasks = [
                search_single_query(client, access_token, query, limit=6)
                for query in search_queries
            ]
            all_results = await asyncio.gather(*genre_tasks, *mood_tasks)

            n_genres = len(explicit_genres)
            genre_results = all_results[:n_genres]
            mood_results = all_results[n_genres:]

            seen = set()
            final_uris = []

            for track_list in genre_results:
                for uri in track_list:
                    if uri not in seen:
                        seen.add(uri)
                        final_uris.append(uri)

            mood_uris = []
            for track_list in mood_results:
                for uri in track_list:
                    if uri not in seen:
                        mood_uris.append(uri)
                        seen.add(uri)
            random.shuffle(mood_uris)
            final_uris.extend(mood_uris)

            print(f"DEBUG genre+mood: {len(final_uris)} tracks")
            return final_uris[:50]

        # CASE 3: No explicit preferences → pure AI mood queries
        print(f"DEBUG pure mood mode: {len(search_queries)} queries")
        mood_queries = search_queries.copy()
        for genre in ai_genres[:4]:
            mood_queries.append(f"{mood} {genre}")

        mood_tasks = [
            search_single_query(client, access_token, query, limit=6)
            for query in mood_queries
        ]
        all_results = await asyncio.gather(*mood_tasks)

        seen = set()
        all_uris = []
        for track_list in all_results:
            for uri in track_list:
                if uri not in seen:
                    seen.add(uri)
                    all_uris.append(uri)

        random.shuffle(all_uris)
        print(f"DEBUG pure mood: {len(all_uris)} tracks")
        return all_uris[:50]


async def create_spotify_playlist(
    access_token: str,
    spotify_user_id: str,
    name: str,
    track_uris: list[str],
) -> dict:
    """
    Creates a private playlist and adds up to 50 tracks.
    Uses /items endpoint — correct replacement for deprecated /tracks.
    """
    async with httpx.AsyncClient() as client:
        create_response = await client.post(
            f"{SPOTIFY_API_URL}/me/playlists",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "name": name,
                "description": "Generated by MoodQueue 🎵",
                "public": False,
                "collaborative": False,
            },
        )

        if create_response.status_code != 201:
            print(f"DEBUG playlist creation error: {create_response.status_code} - {create_response.text}")

        create_response.raise_for_status()
        playlist = create_response.json()
        print(f"DEBUG playlist created: {playlist['id']}")

        await asyncio.sleep(1)

        if track_uris:
            add_response = await client.post(
                f"{SPOTIFY_API_URL}/playlists/{playlist['id']}/items",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"uris": track_uris[:50]},
            )
            if add_response.status_code == 201:
                print(f"DEBUG added {len(track_uris[:50])} tracks successfully")
            else:
                print(f"DEBUG add tracks error: {add_response.status_code} - {add_response.text}")

        return {
            "spotify_playlist_id": playlist["id"],
            "spotify_playlist_url": playlist["external_urls"]["spotify"],
        }