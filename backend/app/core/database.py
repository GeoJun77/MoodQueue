from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# The engine is the actual physical connection to the database.
# echo=True logs every SQL query in the terminal — useful for
# debugging in dev, we'll disable it in production.
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# A session is like an open transaction with the database.
# AsyncSessionLocal is a factory: each call creates a new
# independent session for each incoming HTTP request.
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# All your models (User, Playlist...) will inherit from Base.
# SQLAlchemy uses this to know which tables to create.
class Base(DeclarativeBase):
    pass

# FastAPI dependency: opens a DB session at the start of a request
# and automatically closes it at the end, even if an error occurs.
# The "yield" keyword is what makes this work as a dependency.
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session