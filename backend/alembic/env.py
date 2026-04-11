import sys
from logging.config import fileConfig

from sqlalchemy import create_engine
from alembic import context

# Add /app to the Python path so our imports work inside the container
sys.path.insert(0, '/app')

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic detects them and includes their tables
# in the generated migration — never remove these imports
from app.models import User, MoodEntry, Playlist  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    # asyncpg is for async runtime usage — Alembic runs synchronously,
    # so we swap the driver to the standard psycopg2-compatible one
    return settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

def run_migrations_offline() -> None:
    # "Offline" mode generates SQL scripts without connecting to the DB
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # "Online" mode connects directly to the DB and applies migrations
    connectable = create_engine(get_url())
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()