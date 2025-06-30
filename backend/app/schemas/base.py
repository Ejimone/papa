from pydantic import BaseModel as PydanticBaseModel
from datetime import datetime
from typing import Optional

class BaseModel(PydanticBaseModel):
    class Config:
        from_attributes = True # Replaces orm_mode = True in Pydantic v2

class BaseSchema(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
