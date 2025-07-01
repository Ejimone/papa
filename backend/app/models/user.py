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

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    attempts = relationship("UserAttempt", back_populates="user")
    bookmarks = relationship("UserBookmark", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    analytics = relationship("UserAnalytics", back_populates="user")
    events = relationship("UserEvent", back_populates="user")
    practice_sessions = relationship("PracticeSession", back_populates="user")
    
    # Many-to-many relationships
    subjects = relationship("Subject", secondary="user_subjects", back_populates="enrolled_users")
    study_groups = relationship("StudyGroup", secondary="user_study_groups", back_populates="members")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
