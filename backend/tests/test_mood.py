import pytest

from app.services.catalog import CATALOG, MOODS
from app.services.local_mood import analyze_mood_local, extract_preferences_local


@pytest.mark.parametrize("text,expected", [
    ("Je suis trop nostalgique ce soir, je pense à mon enfance", "nostalgic"),
    ("I need to focus, big exam tomorrow", "focused"),
    ("I need to focus for my exam", "focused"),
    ("I miss my ex so much", "sad"),
    ("Estoy muy triste, lloro todo el día", "sad"),
    ("J'ai le mal du pays, Brazzaville me manque", "homesick"),
    ("On fait la fête ce soir avec les potes !", "party"),
    ("I'm so angry, this is unfair", "angry"),
    ("Besoin de motivation pour la muscu", "motivated"),
    ("Je veux prier et louer Dieu", "spiritual"),
])
def test_local_engine(text, expected):
    result = analyze_mood_local(text)
    assert result["mood"] == expected
    assert 0 < result["confidence"] <= 1
    assert result["explanation"]
    assert result["source"] == "local"


def test_local_engine_unknown_text():
    assert analyze_mood_local("azerty qwerty")["mood"] == "calm"


def test_local_preferences():
    prefs = extract_preferences_local("Mets-moi du Fally Ipupa et du jazz")
    assert "Fally Ipupa" in prefs["artists"]
    assert "jazz" in prefs["genres"]


def test_catalog_complete():
    for mood in MOODS:
        assert len(CATALOG[mood]) >= 10, mood


def test_analyze_endpoint_offline(client, auth):
    r = client.post("/api/mood/analyze",
                    json={"text": "Je suis nostalgique, je repense aux années 2000"}, headers=auth)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["mood"] == "nostalgic"
    assert data["analysis_source"] == "local"
    assert data["playlist_generated"] is True
    assert data["playlist_source"] == "catalog"
    assert len(data["tracks"]) == 15
    t = data["tracks"][0]
    assert t["title"] and t["artist"] and t["youtube_url"].startswith("https://")


def test_analyze_with_artist(client, auth):
    r = client.post("/api/mood/analyze",
                    json={"text": "Je veux danser sur du Aya Nakamura"}, headers=auth)
    tracks = r.json()["tracks"]
    assert any("Aya Nakamura" in t["artist"] for t in tracks[:3])


def test_analyze_validation(client, auth):
    assert client.post("/api/mood/analyze", json={"text": "   "}, headers=auth).status_code == 422
    assert client.post("/api/mood/analyze", json={"text": "hello"}).status_code == 401


def test_history_and_delete(client, auth):
    client.post("/api/mood/analyze", json={"text": "I feel calm and relaxed"}, headers=auth)
    client.post("/api/mood/analyze", json={"text": "Party tonight!"}, headers=auth)
    history = client.get("/api/mood/history", headers=auth).json()
    assert len(history) == 2
    assert history[0]["playlist"]["tracks"]
    playlists = client.get("/api/playlist/history", headers=auth).json()
    assert len(playlists) == 2

    r = client.delete(f"/api/mood/history/{history[0]['id']}", headers=auth)
    assert r.status_code == 204
    assert len(client.get("/api/mood/history", headers=auth).json()) == 1
    assert len(client.get("/api/playlist/history", headers=auth).json()) == 1


def test_spotify_not_configured(client, auth):
    assert client.get("/api/playlist/connect", headers=auth).status_code == 503


def test_spotify_callback_rejects_forged_state(client):
    r = client.get("/api/playlist/callback?code=abc&state=forged", follow_redirects=False)
    assert r.status_code == 302 and "spotify=expired" in r.headers["location"]
