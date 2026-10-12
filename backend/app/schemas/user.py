import re
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


# Data required to create a new account
# EmailStr automatically validates that the email format is correct
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        # Emails are case-insensitive: store them lowercased so
        # "Geo@Mail.com" and "geo@mail.com" are the same account
        return v.strip().lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not USERNAME_RE.match(v):
            raise ValueError(
                "Username must be 3-30 characters (letters, numbers, _ . -)"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # bcrypt only uses the first 72 bytes of a password
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password is too long (max 72 bytes)")
        return v


# Data returned when a user is fetched from the API
# Notice: no password field — we never send it back, even hashed
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    spotify_connected: bool
    created_at: datetime

    # Tells Pydantic to read data from SQLAlchemy objects directly
    model_config = {"from_attributes": True}


# Data required to log in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


# The token returned after a successful login or register
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# The data encoded inside a JWT token
class TokenData(BaseModel):
    user_id: str | None = None
