from datetime import datetime

from pydantic import BaseModel, field_validator


class MoodAnalysisRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def check_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tell me how you feel first")
        if len(v) > 1000:
            raise ValueError("Text is too long (max 1000 characters)")
        return v


class Track(BaseModel):
    title: str
    artist: str
    uri: str | None = None
    spotify_url: str | None = None
    youtube_url: str | None = None
    deezer_url: str | None = None


class MoodAnalysisResponse(BaseModel):
    mood_entry_id: str
    mood: str
    emoji: str = "🎵"
    confidence: float
    explanation: str
    # "ai" (Groq) or "local" (offline engine)
    analysis_source: str = "ai"

    playlist_generated: bool
    playlist_id: str | None = None
    playlist_name: str | None = None
    # Real Spotify playlist link (only when source == "spotify")
    playlist_url: str | None = None
    # "spotify" or "catalog"
    playlist_source: str | None = None
    tracks: list[Track] = []

    created_at: datetime

    model_config = {"from_attributes": True}
