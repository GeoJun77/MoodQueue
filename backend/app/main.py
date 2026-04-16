from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, mood, playlist

# Create the FastAPI application instance.
# docs_url="/docs" enables the auto-generated Swagger UI —
# you can test all your endpoints directly from the browser.
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
)

# CORS middleware is required when your frontend makes requests
# to your backend from a different origin.
# We explicitly list allowed origins instead of using "*"
# because allow_credentials=True is incompatible with wildcard origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mood-queue-one.vercel.app",
        "https://mood-queue-3unktl9es-geo77.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount each router under a URL prefix.
# Example: everything in auth.py is accessible under /api/auth/...
# Tags are used to group endpoints in the Swagger documentation.
app.include_router(auth.router,     prefix="/api/auth",     tags=["auth"])
app.include_router(mood.router,     prefix="/api/mood",     tags=["mood"])
app.include_router(playlist.router, prefix="/api/playlist", tags=["playlist"])

# Health check endpoint — used by Docker and monitoring tools
# to verify the app is running and responsive.
@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}