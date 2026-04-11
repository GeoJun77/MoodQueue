# Import all models here so Alembic can auto-detect them
# when generating migration files.
# If I add a new model later, always import it here —
# otherwise Alembic won't see it and won't create its table.
from app.models.user import User
from app.models.mood_entry import MoodEntry
from app.models.playlist import Playlist

__all__ = ["User", "MoodEntry", "Playlist"]