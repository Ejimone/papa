from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema # For id, created_at, updated_at

# Properties to receive via API on creation
class UserCreate(BaseModel):
    email: str
    username: Optional[str] = None
    password: str = Field(min_length=8)

# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

# Properties stored in DB
class UserInDBBase(BaseSchema): # Inherits id, created_at, updated_at
    email: str
    username: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserInDB(UserInDBBase):
    hashed_password: str

# Properties to return to client
class UserRead(UserInDBBase): # Excludes hashed_password
    pass

# For user profile, can be expanded later
class UserProfile(BaseModel):
    academic_level: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    year: Optional[str] = None
    # subjects: Optional[list[str]] = [] # This would likely be a relationship to a Subject model/schema

class UserProfileUpdate(UserProfile):
    pass
