from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime
import enum

class EventType(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    QUESTION_VIEWED = "question_viewed"
    QUESTION_ANSWERED = "question_answered"
    HINT_REQUESTED = "hint_requested"
    EXPLANATION_VIEWED = "explanation_viewed"
    BOOKMARK_ADDED = "bookmark_added"
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SEARCH_PERFORMED = "search_performed"
    FILTER_APPLIED = "filter_applied"

class PerformanceLevel(str, enum.Enum):
    BEGINNER = "beginner"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"
    EXPERT = "expert"

class UserAnalytics(Base):
    __tablename__ = "user_analytics"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # Date for this analytics record
    
    # Daily activity metrics
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    study_time_minutes = Column(Integer, default=0)
    sessions_count = Column(Integer, default=0)
    login_count = Column(Integer, default=0)
    
    # Performance metrics
    accuracy_rate = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)  # Seconds
    improvement_score = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)
    
    # Learning behavior
    hints_used = Column(Integer, default=0)
    explanations_viewed = Column(Integer, default=0)
    bookmarks_added = Column(Integer, default=0)
    reviews_completed = Column(Integer, default=0)
    
    # Engagement metrics
    app_opens = Column(Integer, default=0)
    feature_usage = Column(JSON, default=dict)  # Track usage of different features
    navigation_patterns = Column(JSON, default=list)  # User navigation flow
    
    # Streaks and achievements
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    achievements_earned = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<UserAnalytics(user_id={self.user_id}, date={self.date}, accuracy={self.accuracy_rate}%)>"

class LearningAnalytics(Base):
    __tablename__ = "learning_analytics"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    
    # Time period
    week_start = Column(DateTime, nullable=False, index=True)
    week_end = Column(DateTime, nullable=False)
    
    # Learning progress
    questions_mastered = Column(Integer, default=0)
    concepts_learned = Column(JSON, default=list)
    difficulty_progression = Column(Float, default=0.0)
    mastery_level = Column(Enum(PerformanceLevel), default=PerformanceLevel.BEGINNER)
    
    # Study patterns
    preferred_study_times = Column(JSON, default=list)  # Hour of day preferences
    session_lengths = Column(JSON, default=list)  # Preferred session durations
    break_patterns = Column(JSON, default=dict)  # How user takes breaks
    
    # Learning efficiency
    learning_velocity = Column(Float, default=0.0)  # Rate of learning new concepts
    retention_rate = Column(Float, default=0.0)  # How well user retains information
    transfer_learning = Column(Float, default=0.0)  # Ability to apply knowledge across topics
    
    # Cognitive load indicators
    mental_effort_score = Column(Float, default=0.0)
    cognitive_load_level = Column(String(20), default="optimal")
    fatigue_indicators = Column(JSON, default=dict)
    
    # Personalization data
    learning_style_indicators = Column(JSON, default=dict)
    optimal_difficulty_level = Column(Float, default=0.5)
    recommended_study_schedule = Column(JSON, default=dict)
    
    # Relationships
    user = relationship("User")
    subject = relationship("Subject")
    topic = relationship("Topic")

    def __repr__(self):
        return f"<LearningAnalytics(user_id={self.user_id}, subject_id={self.subject_id}, week={self.week_start})>"

class QuestionAnalytics(Base):
    __tablename__ = "question_analytics"

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Usage metrics
    views_count = Column(Integer, default=0)
    attempts_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    
    # Performance metrics
    success_rate = Column(Float, default=0.0)
    average_time = Column(Float, default=0.0)
    difficulty_rating = Column(Float, default=0.0)  # User-perceived difficulty
    
    # Engagement metrics
    bookmark_count = Column(Integer, default=0)
    hint_requests = Column(Integer, default=0)
    explanation_views = Column(Integer, default=0)
    skip_rate = Column(Float, default=0.0)
    
    # Quality metrics
    user_ratings = Column(JSON, default=dict)  # User quality ratings
    reported_issues = Column(Integer, default=0)
    improvement_suggestions = Column(JSON, default=list)
    
    # AI-generated insights
    difficulty_accuracy = Column(Float, default=0.0)  # How accurate AI difficulty assessment is
    concept_coverage = Column(Float, default=0.0)  # How well question covers its concepts
    discrimination_index = Column(Float, default=0.0)  # How well question differentiates skill levels
    
    # Relationships
    question = relationship("Question")

    def __repr__(self):
        return f"<QuestionAnalytics(question_id={self.question_id}, date={self.date}, success_rate={self.success_rate}%)>"

class SystemAnalytics(Base):
    __tablename__ = "system_analytics"

    date = Column(DateTime, nullable=False, index=True)
    metric_type = Column(String(50), nullable=False, index=True)  # daily_active_users, api_calls, etc.
    
    # Core metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    
    # Content metrics
    questions_added = Column(Integer, default=0)
    questions_processed = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    
    # Usage metrics
    total_sessions = Column(Integer, default=0)
    total_questions_attempted = Column(Integer, default=0)
    total_study_time = Column(Integer, default=0)  # Minutes
    
    # Performance metrics
    api_response_time_avg = Column(Float, default=0.0)
    api_response_time_p95 = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    uptime_percentage = Column(Float, default=100.0)
    
    # AI metrics
    ai_requests_count = Column(Integer, default=0)
    ai_response_time_avg = Column(Float, default=0.0)
    ai_success_rate = Column(Float, default=0.0)
    
    # Business metrics
    user_retention_1day = Column(Float, default=0.0)
    user_retention_7day = Column(Float, default=0.0)
    user_retention_30day = Column(Float, default=0.0)
    
    # Resource usage
    database_size_mb = Column(Float, default=0.0)
    storage_used_mb = Column(Float, default=0.0)
    bandwidth_used_mb = Column(Float, default=0.0)
    
    # Additional data
    metadata = Column(JSON, default=dict)  # Flexible field for additional metrics

    def __repr__(self):
        return f"<SystemAnalytics(date={self.date}, type='{self.metric_type}', active_users={self.active_users})>"

class UserEvent(Base):
    __tablename__ = "user_events"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Event context
    session_id = Column(String(100), nullable=True, index=True)  # User session ID
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    
    # Event details
    event_data = Column(JSON, default=dict)  # Flexible event-specific data
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)
    
    # Context information
    page_url = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    duration = Column(Float, nullable=True)  # Event duration in seconds
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    question = relationship("Question")
    subject = relationship("Subject")

    def __repr__(self):
        return f"<UserEvent(user_id={self.user_id}, type='{self.event_type}', timestamp={self.timestamp})>"

class PerformanceTrend(Base):
    __tablename__ = "performance_trends"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    
    # Time period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Performance metrics
    questions_attempted = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    improvement_rate = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)
    
    # Time-based metrics
    average_response_time = Column(Float, default=0.0)
    study_time_total = Column(Integer, default=0)
    sessions_count = Column(Integer, default=0)
    
    # Trend indicators
    trend_direction = Column(String(20), nullable=True)  # improving, declining, stable
    trend_strength = Column(Float, default=0.0)  # -1.0 to 1.0
    confidence_interval = Column(Float, default=0.0)
    
    # Predictive metrics
    predicted_next_score = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    factors_influencing = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User")
    subject = relationship("Subject")
    topic = relationship("Topic")

    def __repr__(self):
        return f"<PerformanceTrend(user_id={self.user_id}, period={self.period_start}, trend='{self.trend_direction}')>"
