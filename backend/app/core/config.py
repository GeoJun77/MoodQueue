import secrets
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ folder (this file is backend/app/core/config.py)
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Every setting has a working default, so MoodQueue starts with ZERO
    configuration: SQLite database, local mood engine, built-in music
    catalog. External services (Groq, Spotify, Resend, Postgres) are
    optional upgrades enabled by setting their environment variables.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "MoodQueue"
    DEBUG: bool = False

    # Where local data lives (SQLite file, generated secret key)
    DATA_DIR: Path = BACKEND_DIR / "data"

    # Database — SQLite by default, PostgreSQL if a URL is given
    DATABASE_URL: str = ""

    # JWT signing key. Leave empty to auto-generate one stored in DATA_DIR.
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Groq (LLM) — optional. GROQ_API_KEY preferred, OPENAI_API_KEY kept
    # for backward compatibility with the original deployment.
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    AI_TIMEOUT_SECONDS: float = 15.0

    # Spotify — optional
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8000/api/playlist/callback"

    # Email (password reset) via Resend — optional
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "MoodQueue <onboarding@resend.dev>"

    # Public URL of the web app (used in reset emails and after Spotify login).
    # Empty = same origin as the API (when the backend serves the web app).
    FRONTEND_URL: str = ""

    # Extra allowed CORS origins, comma-separated
    FRONTEND_ORIGINS: str = ""

    # Folder containing the built web app (web/dist). Served if it exists.
    STATIC_DIR: Path = BACKEND_DIR / "static"

    # Kept so old .env files with REDIS_URL don't break anything (unused)
    REDIS_URL: str = ""

    @field_validator("DATABASE_URL")
    @classmethod
    def use_async_driver(cls, v: str) -> str:
        # Railway/Render/Heroku give "postgres://" or "postgresql://" URLs,
        # but SQLAlchemy async needs the asyncpg driver explicitly.
        v = v.strip()
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://"):]
        if v.startswith("postgresql://"):
            v = "postgresql+asyncpg://" + v[len("postgresql://"):]
        if v.startswith("sqlite:///"):
            v = "sqlite+aiosqlite:///" + v[len("sqlite:///"):]
        return v

    @model_validator(mode="after")
    def fill_defaults(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"sqlite+aiosqlite:///{(self.DATA_DIR / 'moodqueue.db').as_posix()}"
        if not self.SECRET_KEY:
            key_file = self.DATA_DIR / ".secret_key"
            if key_file.exists():
                self.SECRET_KEY = key_file.read_text().strip()
            else:
                self.SECRET_KEY = secrets.token_urlsafe(48)
                key_file.write_text(self.SECRET_KEY)
        if not self.GROQ_API_KEY and self.OPENAI_API_KEY.startswith("gsk_"):
            self.GROQ_API_KEY = self.OPENAI_API_KEY
        self.FRONTEND_URL = self.FRONTEND_URL.rstrip("/")
        return self

    # ---- feature flags -------------------------------------------------
    @property
    def ai_enabled(self) -> bool:
        return bool(self.GROQ_API_KEY)

    @property
    def spotify_enabled(self) -> bool:
        return bool(self.SPOTIFY_CLIENT_ID and self.SPOTIFY_CLIENT_SECRET)

    @property
    def email_enabled(self) -> bool:
        return bool(self.RESEND_API_KEY)

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
