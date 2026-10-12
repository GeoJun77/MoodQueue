import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings
from app.core.database import asyncpg_url_and_args

NEON = "postgresql://user:p%40ss@ep-cool-123.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


def test_neon_url_is_normalized_for_asyncpg():
    url = Settings(DATABASE_URL=NEON).DATABASE_URL
    assert url.startswith("postgresql+asyncpg://")
    async_url, args = asyncpg_url_and_args(url)
    assert "sslmode" not in async_url and "channel_binding" not in async_url
    assert "p%40ss" in async_url  # password kept and still escaped
    assert args == {"ssl": "require"}


def test_plain_url_has_no_ssl_args():
    async_url, args = asyncpg_url_and_args("postgresql+asyncpg://u:p@h:5432/d")
    assert async_url == "postgresql+asyncpg://u:p@h:5432/d"
    assert args == {}


def test_asyncpg_accepts_the_cleaned_url():
    # Before the fix asyncpg raised TypeError("unexpected keyword 'sslmode'").
    # Now it must get as far as trying to open a network connection.
    async_url, args = asyncpg_url_and_args(
        "postgresql+asyncpg://u:p@127.0.0.1:1/db?sslmode=require&channel_binding=require"
    )

    async def connect():
        engine = create_async_engine(async_url, connect_args=args)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("select 1"))
        finally:
            await engine.dispose()

    with pytest.raises(OSError):
        asyncio.run(connect())
