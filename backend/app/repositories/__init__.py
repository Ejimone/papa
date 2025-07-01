from .base import BaseRepository
from .user_repository import UserRepository, user_repo
from .question_repository import (
    QuestionRepository, QuestionMetadataRepository, QuestionImageRepository,
    ExplanationRepository, HintRepository, SimilarQuestionRepository,
    question_repo, question_metadata_repo, question_image_repo,
    explanation_repo, hint_repo, similar_question_repo
)
from .subject_repository import SubjectRepository, TopicRepository, subject_repo, topic_repo
from .practice_repository import (
    PracticeSessionRepository, UserAttemptRepository, UserBookmarkRepository,
    UserProgressRepository, UserProfileRepository, UserPreferencesRepository,
    practice_session_repo, user_attempt_repo, user_bookmark_repo,
    user_progress_repo, user_profile_repo, user_preferences_repo
)
from .analytics_repository import (
    DailyUserActivityRepository, WeeklyUserActivityRepository, MonthlyUserActivityRepository,
    SubjectPerformanceAnalyticsRepository, TopicPerformanceAnalyticsRepository,
    DifficultyLevelAnalyticsRepository, LearningPathAnalyticsRepository,
    AnalyticsRepository, analytics_repo, daily_activity_repo, weekly_activity_repo,
    monthly_activity_repo, subject_performance_repo, topic_performance_repo,
    difficulty_analytics_repo, learning_path_repo
)

__all__ = [
    # Base
    "BaseRepository",
    
    # User repositories
    "UserRepository",
    "user_repo",
    
    # Question repositories
    "QuestionRepository",
    "QuestionMetadataRepository", 
    "QuestionImageRepository",
    "ExplanationRepository",
    "HintRepository",
    "SimilarQuestionRepository",
    "question_repo",
    "question_metadata_repo",
    "question_image_repo",
    "explanation_repo", 
    "hint_repo",
    "similar_question_repo",
    
    # Subject repositories
    "SubjectRepository",
    "TopicRepository", 
    "subject_repo",
    "topic_repo",
    
    # Practice repositories
    "PracticeSessionRepository",
    "UserAttemptRepository",
    "UserBookmarkRepository",
    "UserProgressRepository",
    "UserProfileRepository",
    "UserPreferencesRepository",
    "practice_session_repo",
    "user_attempt_repo",
    "user_bookmark_repo",
    "user_progress_repo",
    "user_profile_repo",
    "user_preferences_repo",
    
    # Analytics repositories
    "DailyUserActivityRepository",
    "WeeklyUserActivityRepository",
    "MonthlyUserActivityRepository",
    "SubjectPerformanceAnalyticsRepository",
    "TopicPerformanceAnalyticsRepository", 
    "DifficultyLevelAnalyticsRepository",
    "LearningPathAnalyticsRepository",
    "AnalyticsRepository",
    "analytics_repo",
    "daily_activity_repo",
    "weekly_activity_repo",
    "monthly_activity_repo",
    "subject_performance_repo",
    "topic_performance_repo",
    "difficulty_analytics_repo",
    "learning_path_repo",
]
