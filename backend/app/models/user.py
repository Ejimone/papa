from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base # Corrected import path from app.core.db to app.models.base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    # id = Column(Integer, primary_key=True, index=True) # Inherited from Base
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True) # Optional username
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    # last_login_at = Column(DateTime, nullable=True) # Can be added later

    # created_at = Column(DateTime, default=datetime.utcnow) # Inherited from Base
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Inherited from Base

    # Relationships - can be added as needed, e.g.
    # profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # attempts = relationship("UserAttempt", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
