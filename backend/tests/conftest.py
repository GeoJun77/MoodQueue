import os
import tempfile

import pytest

# Isolated, offline configuration: no external service is ever called.
_tmp = tempfile.mkdtemp(prefix="moodqueue-test-")
os.environ.update(
    DATA_DIR=_tmp,
    # Set TEST_DATABASE_URL to run the suite against PostgreSQL
    DATABASE_URL=os.environ.get("TEST_DATABASE_URL", f"sqlite+aiosqlite:///{_tmp}/test.db"),
    SECRET_KEY="test-secret-key-that-is-long-enough-1234567890",
    GROQ_API_KEY="",
    OPENAI_API_KEY="",
    SPOTIFY_CLIENT_ID="",
    SPOTIFY_CLIENT_SECRET="",
    RESEND_API_KEY="",
    STATIC_DIR=os.path.join(_tmp, "no-static"),
)

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:  # runs startup (migrations)
        yield c


_counter = iter(range(10_000))


@pytest.fixture
def auth(client):
    """Registers a fresh user and returns its Authorization header."""
    n = next(_counter)
    r = client.post(
        "/api/auth/register",
        json={"email": f"user{n}@test.com", "username": f"user_{n}", "password": "password123"},
    )
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
