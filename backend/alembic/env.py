import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import create_engine
from alembic import context

# Make "import app" work whatever the current directory is
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic sees their tables — never remove
from app.models import User, MoodEntry, Playlist  # noqa: F401

config = context.config
# When the app runs migrations at startup it keeps its own logging setup
if config.config_file_name is not None and not config.attributes.get("skip_logging"):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def get_url() -> str:
    # Alembic runs synchronously: swap async drivers for sync ones
    url = settings.DATABASE_URL
    url = url.replace("postgresql+asyncpg", "postgresql")
    url = url.replace("sqlite+aiosqlite", "sqlite")
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=url.startswith("sqlite"),
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite can't ALTER most things; batch mode recreates tables
            render_as_batch=url.startswith("sqlite"),
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
