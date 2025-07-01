from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

# Enums (these should match the models)
class SessionType(str, Enum):
    QUICK_PRACTICE = "quick_practice"
    TARGETED_STUDY = "targeted_study"
    MOCK_TEST = "mock_test"
    REVIEW_SESSION = "review_session"

class SessionStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class AttemptStatus(str, Enum):
    ANSWERED = "answered"
    SKIPPED = "skipped"
    FLAGGED = "flagged"

# Base schemas
class PracticeSessionBase(BaseModel):
    session_type: SessionType
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    difficulty_level: Optional[str] = None
    target_questions: Optional[int] = 10
    time_limit_minutes: Optional[int] = None

class PracticeSessionCreate(PracticeSessionBase):
    pass

class PracticeSessionUpdate(BaseModel):
    status: Optional[SessionStatus] = None
    correct_answers: Optional[int] = None
    incorrect_answers: Optional[int] = None
    skipped_questions: Optional[int] = None
    total_time_spent: Optional[int] = None
    score_percentage: Optional[float] = None
    average_time_per_question: Optional[float] = None
    
class PracticeSessionRead(PracticeSessionBase):
    id: int
    user_id: int
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_questions: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    skipped_questions: int = 0
    total_time_spent: int = 0
    score_percentage: Optional[float] = None
    average_time_per_question: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Attempt schemas
class UserAttemptBase(BaseModel):
    question_id: int
    session_id: Optional[int] = None
    answer: Optional[str] = None
    is_correct: Optional[bool] = None
    time_taken: Optional[float] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=5)
    hint_used: bool = False
    explanation_viewed: bool = False
    status: AttemptStatus = AttemptStatus.ANSWERED

class UserAttemptCreate(UserAttemptBase):
    pass

class UserAttemptUpdate(BaseModel):
    answer: Optional[str] = None
    is_correct: Optional[bool] = None
    time_taken: Optional[float] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=5)
    hint_used: Optional[bool] = None
    explanation_viewed: Optional[bool] = None
    status: Optional[AttemptStatus] = None

class UserAttemptRead(UserAttemptBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# User Bookmark schemas
class UserBookmarkBase(BaseModel):
    question_id: int
    bookmark_type: str = "general"
    notes: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)
    tags: Optional[List[str]] = []

class UserBookmarkCreate(UserBookmarkBase):
    pass

class UserBookmarkUpdate(BaseModel):
    bookmark_type: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_mastered: Optional[bool] = None

class UserBookmarkRead(UserBookmarkBase):
    id: int
    user_id: int
    is_active: bool = True
    is_mastered: bool = False
    review_count: int = 0
    last_reviewed_at: Optional[datetime] = None
    target_review_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# User Progress schemas
class UserProgressBase(BaseModel):
    subject_id: int
    topic_id: Optional[int] = None

class UserProgressCreate(UserProgressBase):
    pass

class UserProgressUpdate(BaseModel):
    total_questions_attempted: Optional[int] = None
    correct_answers: Optional[int] = None
    incorrect_answers: Optional[int] = None
    accuracy_rate: Optional[float] = None
    average_time_per_question: Optional[float] = None
    mastery_level: Optional[float] = None
    streak_count: Optional[int] = None

class UserProgressRead(UserProgressBase):
    id: int
    user_id: int
    total_questions_attempted: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    accuracy_rate: float = 0.0
    average_time_per_question: Optional[float] = None
    mastery_level: float = 0.0
    streak_count: int = 0
    last_practiced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Profile schemas
class UserProfileBase(BaseModel):
    university: Optional[str] = None
    degree: Optional[str] = None
    year_of_study: Optional[int] = Field(None, ge=1, le=10)
    major: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileRead(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Preferences schemas
class UserPreferencesBase(BaseModel):
    study_reminders: bool = True
    email_notifications: bool = True
    push_notifications: bool = True
    difficulty_preference: Optional[str] = "medium"
    study_goals: Optional[Dict[str, Any]] = {}
    preferred_study_time: Optional[str] = None
    theme: str = "light"
    language: str = "en"

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesUpdate(UserPreferencesBase):
    pass

class UserPreferencesRead(UserPreferencesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
