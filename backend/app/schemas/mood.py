from pydantic import BaseModel
from datetime import datetime

class MoodAnalysisRequest(BaseModel):
    # The raw text the user types to describe their mood
    # e.g. "feeling super nostalgic tonight, miss my childhood"
    text: str

class MoodAnalysisResponse(BaseModel):
    # The mood entry ID saved in the database
    mood_entry_id: str

    # The detected mood label
    mood: str

    # Confidence score between 0.0 and 1.0
    confidence: float

    # Short explanation from the AI
    explanation: str

    # Whether a Spotify playlist was generated
    playlist_generated: bool

    # Spotify playlist URL if generated
    playlist_url: str | None = None

    # The generated playlist name
    playlist_name: str | None = None

    created_at: datetime

    model_config = {"from_attributes": True}