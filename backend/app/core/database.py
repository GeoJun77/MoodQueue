import asyncio
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.engine import make_url

from app.core.config import settings, BACKEND_DIR


def asyncpg_url_and_args(url: str) -> tuple[str, dict]:
    """
    Hosted Postgres (Neon, Supabase, Render...) gives libpq-style URLs like
    ...?sslmode=require&channel_binding=require. asyncpg rejects those
    parameters, so we strip them and translate sslmode into asyncpg's `ssl`.
    (Alembic uses psycopg2, which understands them, so it keeps the raw URL.)
    """
    u = make_url(url)
    query = dict(u.query)
    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)
    connect_args: dict = {}
    if sslmode:
        # asyncpg accepts the same mode names as libpq
        connect_args["ssl"] = sslmode
    return u.set(query=query).render_as_string(hide_password=False), connect_args

# The engine is the physical connection to the database.
# SQLite needs a couple of tweaks; Postgres gets pool_pre_ping so
# connections silently dropped by a hosted DB are recycled.
if settings.is_sqlite:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _sqlite_pragmas(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA journal_mode=WAL")
        cur.close()
else:
    async_url, pg_connect_args = asyncpg_url_and_args(settings.DATABASE_URL)
    engine = create_async_engine(
        async_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        connect_args=pg_connect_args,
    )

# Each call creates an independent session for one HTTP request
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: one DB session per request, always closed."""
    async with AsyncSessionLocal() as session:
        yield session


def _run_migrations() -> None:
    # Alembic is the single source of truth for the schema, for both
    # SQLite and PostgreSQL. Running it at startup means a fresh clone
    # (or a 20-year-old database) is always brought up to date.
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.attributes["skip_logging"] = True
    command.upgrade(cfg, "head")


async def init_db() -> None:
    await asyncio.to_thread(_run_migrations)
