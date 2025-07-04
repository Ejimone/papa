# Import base first
from .base import Base

# Import all models
from .user import User, UserProfile, UserPreferences
from .subject import Subject, Topic
from .course_material import CourseMaterial
from .question import (
    Question, QuestionMetadata, QuestionImage, 
    Explanation, Hint, SimilarQuestion,
    QuestionType, DifficultyLevel
)
from .practice import (
    PracticeSession, UserAttempt, UserBookmark, 
    UserProgress,
    SessionType, SessionStatus, AttemptStatus
)
from .analytics import (
    UserAnalytics, LearningAnalytics, QuestionAnalytics, 
    SystemAnalytics, UserEvent, PerformanceTrend,
    EventType, PerformanceLevel,
    DailyUserActivity, WeeklyUserActivity, MonthlyUserActivity,
    SubjectPerformanceAnalytics, TopicPerformanceAnalytics,
    DifficultyLevelAnalytics, LearningPathAnalytics
)
from .associations import (
    StudyGroup, user_subjects, user_topic_interests, 
    question_tags, user_study_groups
)

# Export all models for easy import
__all__ = [
    # Base
    "Base",
    
    # User models
    "User", "UserProfile", "UserPreferences",
    
    # Subject models
    "Subject", "Topic",
    
    # Course material models
    "CourseMaterial",
    
    # Question models
    "Question", "QuestionMetadata", "QuestionImage",
    "Explanation", "Hint", "SimilarQuestion",
    "QuestionType", "DifficultyLevel",
    
    # Practice models
    "PracticeSession", "UserAttempt", "UserBookmark", "UserProgress",
    "SessionType", "SessionStatus", "AttemptStatus",
    
    # Analytics models
    "UserAnalytics", "LearningAnalytics", "QuestionAnalytics",
    "SystemAnalytics", "UserEvent", "PerformanceTrend",
    "EventType", "PerformanceLevel",
    "DailyUserActivity", "WeeklyUserActivity", "MonthlyUserActivity",
    "SubjectPerformanceAnalytics", "TopicPerformanceAnalytics",
    "DifficultyLevelAnalytics", "LearningPathAnalytics",
    
    # Association models
    "StudyGroup", "user_subjects", "user_topic_interests",
    "question_tags", "user_study_groups",
]
