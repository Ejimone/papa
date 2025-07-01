from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base # Corrected import path from app.core.db to app.models.base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True) # Optional username
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
        return f"<User(email='{self.email}', full_name='{self.full_name}')>"


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    academic_level = Column(String(50), nullable=True)  # e.g., "undergraduate", "graduate"
    institution = Column(String(200), nullable=True)
    field_of_study = Column(String(100), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, name='{self.institution}')>"


class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Learning preferences
    preferred_difficulty = Column(String(20), default="medium")  # easy, medium, hard
    daily_question_goal = Column(Integer, default=10)
    study_reminder_enabled = Column(Boolean, default=True)
    study_reminder_time = Column(String(5), default="09:00")  # HH:MM format
    
    # UI preferences
    dark_mode = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    
    # Practice preferences
    show_explanations_immediately = Column(Boolean, default=False)
    shuffle_answers = Column(Boolean, default=True)
    time_limit_enabled = Column(Boolean, default=False)
    default_time_limit = Column(Integer, default=60)  # seconds per question
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, difficulty='{self.preferred_difficulty}')>"
