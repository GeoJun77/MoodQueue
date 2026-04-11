from pydantic_settings import BaseSettings

# BaseSettings automatically reads variables from your .env file
# and validates them at startup. If a required variable is missing,
# the app refuses to start — prevents running a misconfigured server.
class Settings(BaseSettings):
    APP_NAME: str = "MoodQueue"
    DEBUG: bool = False

    # Full connection URL to PostgreSQL.
    # Format: driver://user:password@host:port/database_name
    DATABASE_URL: str

    # Redis connection URL (used for cache and sessions)
    REDIS_URL: str = "redis://redis:6379"

    # Secret key used to sign JWT tokens.
    # Must be long and random — never share or commit this.
    SECRET_KEY: str

    # Algorithm used to encode JWT tokens
    ALGORITHM: str = "HS256"

    # Token lifetime: 24 hours (60 min × 24)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # OpenAI API key for mood analysis
    OPENAI_API_KEY: str

    # Spotify app credentials (we'll create these in step 5)
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    # URL Spotify will redirect to after the user grants access
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/api/playlist/callback"

    class Config:
        # Tells Pydantic where to look for the config file
        env_file = ".env"

# Single instance imported everywhere in the app.
# This is the "singleton" pattern — one source of truth.
settings = Settings()