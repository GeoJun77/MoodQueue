import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, mood, playlist
from app.core.config import settings
from app.core.database import init_db

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("moodqueue")

VERSION = "2.0.0"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create / upgrade the database schema before serving requests
    await init_db()
    log.info(
        "MoodQueue %s ready — database: %s | AI: %s | Spotify: %s | email: %s",
        VERSION,
        "SQLite" if settings.is_sqlite else "PostgreSQL",
        "Groq" if settings.ai_enabled else "offline engine",
        "on" if settings.spotify_enabled else "off (built-in catalog)",
        "on" if settings.email_enabled else "off (links in logs)",
    )
    yield


app = FastAPI(title=settings.APP_NAME, version=VERSION, docs_url="/docs", lifespan=lifespan)

# CORS: only needed when the web app is hosted on another domain (e.g. Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://mood-queue-one.vercel.app",
        *[o.strip() for o in settings.FRONTEND_ORIGINS.split(",") if o.strip()],
    ],
    # Every Vercel preview deployment of the project (mood-queue-xxxx.vercel.app)
    allow_origin_regex=r"https://mood-queue-[a-z0-9-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(mood.router, prefix="/api/mood", tags=["mood"])
app.include_router(playlist.router, prefix="/api/playlist", tags=["playlist"])


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": VERSION}


@app.get("/api/status")
async def status():
    """Which optional features are active — the web app adapts its UI to this."""
    return {
        "version": VERSION,
        "features": {
            "ai": settings.ai_enabled,
            "spotify": settings.spotify_enabled,
            "email": settings.email_enabled,
        },
    }


# ---- Serve the built web app (web/dist copied to backend/static) ---------
# One server = API + website. Unknown paths return index.html so React
# Router can handle /history, /reset-password, etc.
static_dir = settings.STATIC_DIR
if (static_dir / "index.html").exists():
    if (static_dir / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str):
        if path.startswith(("api/", "docs", "openapi.json")):
            raise HTTPException(status_code=404)
        file = (static_dir / path).resolve()
        if path and file.is_file() and static_dir.resolve() in file.parents:
            return FileResponse(file)
        return FileResponse(static_dir / "index.html")
