import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # SET NULL instead of CASCADE — if the mood entry is deleted,
    # we keep the playlist but just lose the reference to its origin
    mood_entry_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("mood_entries.id", ondelete="SET NULL"), nullable=True
    )

    # The mood label used to generate this playlist
    mood_label: Mapped[str] = mapped_column(String, nullable=False)

    # Spotify identifiers — used to build the shareable link
    spotify_playlist_id: Mapped[str | None] = mapped_column(String, nullable=True)
    spotify_playlist_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # A generated name for the playlist
    # e.g. "Your nostalgic sunday evening 🌙"
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Track IDs stored as a JSON array — avoids needing a separate tracks table
    # e.g. ["spotify:track:abc123", "spotify:track:def456"]
    track_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)

    track_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="playlists")
    mood_entry: Mapped["MoodEntry | None"] = relationship(
        "MoodEntry", back_populates="playlist"
    )