from pydantic import BaseModel, EmailStr
from datetime import datetime

# Data required to create a new account
# EmailStr automatically validates that the email format is correct
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

# Data returned when a user is fetched from the API
# Notice: no password field — we never send it back, even hashed
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    spotify_connected: bool
    created_at: datetime

    # Tells Pydantic to read data from SQLAlchemy objects directly
    # Without this, Pydantic wouldn't know how to read ORM attributes
    model_config = {"from_attributes": True}

# Data required to log in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# The token returned after a successful login or register
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# The data encoded inside a JWT token
class TokenData(BaseModel):
    user_id: str | None = None