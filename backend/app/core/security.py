from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# CryptContext handles password hashing using bcrypt.
# bcrypt is the industry standard — it's slow on purpose,
# which makes brute-force attacks very expensive.
# "deprecated=auto" means older hash schemes are auto-upgraded.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Takes a plain password and returns its bcrypt hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plain password against a stored hash.
    Returns True if they match, False otherwise.
    Never compare passwords directly with == — always use this.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    """
    Creates a signed JWT token containing the user's ID.
    The token expires after ACCESS_TOKEN_EXPIRE_MINUTES (24h by default).
    Anyone with the SECRET_KEY can verify the token — keep it secret.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # The payload is the data encoded inside the token
    # "sub" (subject) is the standard JWT claim for the user identifier
    payload = {
        "sub": user_id,
        "exp": expire,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> str | None:
    """
    Decodes a JWT token and returns the user_id inside it.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        # Invalid signature, expired token, malformed token — all caught here
        return None