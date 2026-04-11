import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Foreign key — links this entry to its owner.
    # ondelete="CASCADE" means if the user is deleted,
    # their mood entries are automatically deleted too
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # The raw text the user typed to describe their mood
    # e.g. "feeling nostalgic and melancholic tonight"
    raw_text: Mapped[str] = mapped_column(String, nullable=False)

    # The mood label extracted by OpenAI
    # e.g. "nostalgic", "energetic", "sad", "happy"
    detected_mood: Mapped[str | None] = mapped_column(String, nullable=True)

    # Confidence score returned by OpenAI — float between 0.0 and 1.0
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Full OpenAI response stored as JSON — useful for debugging
    # and adding features later without changing the schema
    raw_ai_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # back_populates tells SQLAlchemy both sides of the relationship
    user: Mapped["User"] = relationship("User", back_populates="mood_entries")

    # uselist=False = one-to-one: one mood entry generates one playlist
    playlist: Mapped["Playlist | None"] = relationship(
        "Playlist", back_populates="mood_entry", uselist=False
    )