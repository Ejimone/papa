from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None # Optional: if you implement refresh tokens
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None # Subject (user identifier, e.g., email or id)
    exp: Optional[int] = None # Expiry timestamp

class LoginRequest(BaseModel):
    email: str # Or username, depending on login preference
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
