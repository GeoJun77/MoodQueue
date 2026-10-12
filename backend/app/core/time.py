from datetime import datetime, timezone


def utcnow() -> datetime:
    """Naive UTC datetime (what the DB columns store).
    Replaces datetime.utcnow(), which Python is removing."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
