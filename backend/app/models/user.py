import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class User(Base):
    # The actual table name in PostgreSQL
    __tablename__ = "users"

    # UUID is better than auto-increment integers:
    # harder to guess, safe to expose in URLs,
    # and works across distributed systems
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # index=True adds a DB index — makes lookups by email much faster
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # We NEVER store a plain password — only the bcrypt hash
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Tracks whether the user has linked their Spotify account via OAuth
    spotify_connected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Spotify tokens saved so the user doesn't have to re-login every time
    spotify_access_token: Mapped[str | None] = mapped_column(String, nullable=True)
    spotify_refresh_token: Mapped[str | None] = mapped_column(String, nullable=True)

    # Password reset token — generated when user requests a reset
    # Stored as a UUID string, cleared after use
    reset_token: Mapped[str | None] = mapped_column(String, nullable=True)

    # Expiry date of the reset token — valid for 1 hour
    reset_token_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # SQLAlchemy relationships — lets you write user.mood_entries in Python
    # instead of writing a JOIN query in SQL
    # cascade="all, delete-orphan" means if a user is deleted,
    # all their entries and playlists are deleted too
    mood_entries: Mapped[list["MoodEntry"]] = relationship(
        "MoodEntry", back_populates="user", cascade="all, delete-orphan"
    )
    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist", back_populates="user", cascade="all, delete-orphan"
    )