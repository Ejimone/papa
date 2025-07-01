from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator

# Define enums locally to avoid import issues
class EventType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    QUESTION_VIEW = "question_view"
    QUESTION_ATTEMPT = "question_attempt"
    SESSION_START = "session_start"
    SESSION_END = "session_end"

class PerformanceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# Base schema class
class BaseSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Analytics Schemas
class UserAnalyticsBase(BaseModel):
    date: date
    questions_attempted: int = Field(default=0, ge=0)
    questions_correct: int = Field(default=0, ge=0)
    study_time_minutes: int = Field(default=0, ge=0)
    sessions_count: int = Field(default=0, ge=0)
    login_count: int = Field(default=0, ge=0)
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_response_time: float = Field(default=0.0, ge=0.0)
    improvement_score: float = Field(default=0.0, ge=-100.0, le=100.0)
    consistency_score: float = Field(default=0.0, ge=0.0, le=100.0)
    hints_used: int = Field(default=0, ge=0)
    explanations_viewed: int = Field(default=0, ge=0)
    bookmarks_added: int = Field(default=0, ge=0)
    reviews_completed: int = Field(default=0, ge=0)
    app_opens: int = Field(default=0, ge=0)
    feature_usage: Dict[str, int] = {}
    navigation_patterns: List[str] = []
    current_streak: int = Field(default=0, ge=0)
    longest_streak: int = Field(default=0, ge=0)
    achievements_earned: List[str] = []

class UserAnalyticsCreate(UserAnalyticsBase):
    user_id: int

class UserAnalyticsUpdate(BaseModel):
    questions_attempted: Optional[int] = Field(None, ge=0)
    questions_correct: Optional[int] = Field(None, ge=0)
    study_time_minutes: Optional[int] = Field(None, ge=0)
    sessions_count: Optional[int] = Field(None, ge=0)
    login_count: Optional[int] = Field(None, ge=0)
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    average_response_time: Optional[float] = Field(None, ge=0.0)
    improvement_score: Optional[float] = Field(None, ge=-100.0, le=100.0)
    consistency_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    hints_used: Optional[int] = Field(None, ge=0)
    explanations_viewed: Optional[int] = Field(None, ge=0)
    bookmarks_added: Optional[int] = Field(None, ge=0)
    reviews_completed: Optional[int] = Field(None, ge=0)
    app_opens: Optional[int] = Field(None, ge=0)
    feature_usage: Optional[Dict[str, int]] = None
    navigation_patterns: Optional[List[str]] = None
    current_streak: Optional[int] = Field(None, ge=0)
    longest_streak: Optional[int] = Field(None, ge=0)
    achievements_earned: Optional[List[str]] = None

class UserAnalyticsRead(BaseSchema):
    user_id: int
    date: datetime
    questions_attempted: int
    questions_correct: int
    study_time_minutes: int
    sessions_count: int
    login_count: int
    accuracy_rate: float
    average_response_time: float
    improvement_score: float
    consistency_score: float
    hints_used: int
    explanations_viewed: int
    bookmarks_added: int
    reviews_completed: int
    app_opens: int
    feature_usage: Dict[str, int]
    navigation_patterns: List[str]
    current_streak: int
    longest_streak: int
    achievements_earned: List[str]

# Learning Analytics Schemas
class LearningAnalyticsBase(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    learning_efficiency: float = 0.0
    time_spent_learning: int = 0  # minutes
    concepts_mastered: int = 0
    concepts_struggling: int = 0
    study_consistency_score: float = 0.0
    engagement_score: float = 0.0

class LearningAnalyticsCreate(LearningAnalyticsBase):
    pass

class LearningAnalyticsUpdate(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[int] = None
    learning_efficiency: Optional[float] = None
    time_spent_learning: Optional[int] = None
    concepts_mastered: Optional[int] = None
    concepts_struggling: Optional[int] = None
    study_consistency_score: Optional[float] = None
    engagement_score: Optional[float] = None

class LearningAnalyticsRead(LearningAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Question Analytics Schemas
class QuestionAnalyticsBase(BaseModel):
    date: date
    views_count: int = Field(default=0, ge=0)
    attempts_count: int = Field(default=0, ge=0)
    unique_users: int = Field(default=0, ge=0)
    success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_time: float = Field(default=0.0, ge=0.0)
    difficulty_rating: float = Field(default=0.0, ge=0.0, le=10.0)
    bookmark_count: int = Field(default=0, ge=0)
    hint_requests: int = Field(default=0, ge=0)
    explanation_views: int = Field(default=0, ge=0)
    skip_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    user_ratings: Dict[str, Any] = {}
    reported_issues: int = Field(default=0, ge=0)
    improvement_suggestions: List[str] = []
    difficulty_accuracy: float = Field(default=0.0, ge=0.0, le=100.0)
    concept_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    discrimination_index: float = Field(default=0.0, ge=-1.0, le=1.0)

class QuestionAnalyticsCreate(QuestionAnalyticsBase):
    question_id: int

class QuestionAnalyticsRead(BaseSchema):
    question_id: int
    date: datetime
    views_count: int
    attempts_count: int
    unique_users: int
    success_rate: float
    average_time: float
    difficulty_rating: float
    bookmark_count: int
    hint_requests: int
    explanation_views: int
    skip_rate: float
    user_ratings: Dict[str, Any]
    reported_issues: int
    improvement_suggestions: List[str]
    difficulty_accuracy: float
    concept_coverage: float
    discrimination_index: float

# System Analytics Schemas
class SystemAnalyticsBase(BaseModel):
    date: date
    metric_type: str
    total_users: int = Field(default=0, ge=0)
    active_users: int = Field(default=0, ge=0)
    new_users: int = Field(default=0, ge=0)
    returning_users: int = Field(default=0, ge=0)
    questions_added: int = Field(default=0, ge=0)
    questions_processed: int = Field(default=0, ge=0)
    total_questions: int = Field(default=0, ge=0)
    total_sessions: int = Field(default=0, ge=0)
    total_questions_attempted: int = Field(default=0, ge=0)
    total_study_time: int = Field(default=0, ge=0)  # minutes
    api_response_time_avg: float = Field(default=0.0, ge=0.0)
    api_response_time_p95: float = Field(default=0.0, ge=0.0)
    error_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    uptime_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    ai_requests_count: int = Field(default=0, ge=0)
    ai_response_time_avg: float = Field(default=0.0, ge=0.0)
    ai_success_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    user_retention_1day: float = Field(default=0.0, ge=0.0, le=100.0)
    user_retention_7day: float = Field(default=0.0, ge=0.0, le=100.0)
    user_retention_30day: float = Field(default=0.0, ge=0.0, le=100.0)
    database_size_mb: float = Field(default=0.0, ge=0.0)
    storage_used_mb: float = Field(default=0.0, ge=0.0)
    bandwidth_used_mb: float = Field(default=0.0, ge=0.0)
    additional_data: Dict[str, Any] = {}

class SystemAnalyticsCreate(SystemAnalyticsBase):
    pass

class SystemAnalyticsRead(BaseSchema):
    date: datetime
    metric_type: str
    total_users: int
    active_users: int
    new_users: int
    returning_users: int
    questions_added: int
    questions_processed: int
    total_questions: int
    total_sessions: int
    total_questions_attempted: int
    total_study_time: int
    api_response_time_avg: float
    api_response_time_p95: float
    error_rate: float
    uptime_percentage: float
    ai_requests_count: int
    ai_response_time_avg: float
    ai_success_rate: float
    user_retention_1day: float
    user_retention_7day: float
    user_retention_30day: float
    database_size_mb: float
    storage_used_mb: float
    bandwidth_used_mb: float
    additional_data: Dict[str, Any]

# User Event Schemas
class UserEventBase(BaseModel):
    event_type: EventType
    session_id: Optional[str] = Field(None, max_length=100)
    question_id: Optional[int] = None
    subject_id: Optional[int] = None
    event_data: Dict[str, Any] = {}
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=50)
    device_type: Optional[str] = Field(None, max_length=50)
    page_url: Optional[str] = Field(None, max_length=500)
    referrer: Optional[str] = Field(None, max_length=500)
    duration: Optional[float] = Field(None, ge=0.0)

class UserEventCreate(UserEventBase):
    user_id: int

class UserEventRead(BaseSchema):
    user_id: int
    event_type: EventType
    timestamp: datetime
    session_id: Optional[str]
    question_id: Optional[int]
    subject_id: Optional[int]
    event_data: Dict[str, Any]
    user_agent: Optional[str]
    ip_address: Optional[str]
    device_type: Optional[str]
    page_url: Optional[str]
    referrer: Optional[str]
    duration: Optional[float]
    is_processed: bool
    processed_at: Optional[datetime]

# Performance Trend Schemas
class PerformanceTrendBase(BaseModel):
    period_start: date
    period_end: date
    period_type: str  # daily, weekly, monthly
    questions_attempted: int = Field(default=0, ge=0)
    accuracy_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    improvement_rate: float = Field(default=0.0, ge=-100.0, le=100.0)
    consistency_score: float = Field(default=0.0, ge=0.0, le=100.0)
    average_response_time: float = Field(default=0.0, ge=0.0)
    study_time_total: int = Field(default=0, ge=0)
    sessions_count: int = Field(default=0, ge=0)
    trend_direction: Optional[str] = None
    trend_strength: float = Field(default=0.0, ge=-1.0, le=1.0)
    confidence_interval: float = Field(default=0.0, ge=0.0, le=100.0)
    predicted_next_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    confidence_level: Optional[float] = Field(None, ge=0.0, le=100.0)
    factors_influencing: List[str] = []

    @validator('period_type')
    def validate_period_type(cls, v):
        valid_types = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        if v not in valid_types:
            raise ValueError(f'Period type must be one of: {valid_types}')
        return v

    @validator('trend_direction')
    def validate_trend_direction(cls, v):
        if v is not None:
            valid_directions = ['improving', 'declining', 'stable', 'fluctuating']
            if v not in valid_directions:
                raise ValueError(f'Trend direction must be one of: {valid_directions}')
        return v

class PerformanceTrendCreate(PerformanceTrendBase):
    user_id: int
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None

class PerformanceTrendRead(BaseSchema):
    user_id: int
    subject_id: Optional[int]
    topic_id: Optional[int]
    period_start: datetime
    period_end: datetime
    period_type: str
    questions_attempted: int
    accuracy_rate: float
    improvement_rate: float
    consistency_score: float
    average_response_time: float
    study_time_total: int
    sessions_count: int
    trend_direction: Optional[str]
    trend_strength: float
    confidence_interval: float
    predicted_next_score: Optional[float]
    confidence_level: Optional[float]
    factors_influencing: List[str]

# Analytics Query and Filter Schemas
class AnalyticsDateRange(BaseModel):
    start_date: date
    end_date: date

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class UserAnalyticsFilter(BaseModel):
    date_range: Optional[AnalyticsDateRange] = None
    user_ids: Optional[List[int]] = None
    min_accuracy: Optional[float] = Field(None, ge=0.0, le=100.0)
    max_accuracy: Optional[float] = Field(None, ge=0.0, le=100.0)
    min_questions: Optional[int] = Field(None, ge=0)
    max_questions: Optional[int] = Field(None, ge=0)
    min_study_time: Optional[int] = Field(None, ge=0)  # minutes
    max_study_time: Optional[int] = Field(None, ge=0)
    streak_min: Optional[int] = Field(None, ge=0)

class AnalyticsAggregation(BaseModel):
    group_by: List[str] = []  # ['date', 'subject', 'topic', 'user']
    aggregation_period: str = Field(default="daily")  # daily, weekly, monthly
    metrics: List[str] = []  # Which metrics to calculate
    include_trends: bool = False
    include_predictions: bool = False

    @validator('aggregation_period')
    def validate_aggregation_period(cls, v):
        valid_periods = ['hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        if v not in valid_periods:
            raise ValueError(f'Aggregation period must be one of: {valid_periods}')
        return v

class AnalyticsQuery(BaseModel):
    filters: Optional[UserAnalyticsFilter] = None
    aggregation: Optional[AnalyticsAggregation] = None
    limit: int = Field(default=100, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="date")
    sort_order: str = Field(default="desc")

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v

# Dashboard Schemas
class DashboardData(BaseModel):
    user_id: int
    date_range: AnalyticsDateRange
    overview: Dict[str, Any]
    performance_summary: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    progress_charts: Dict[str, Any]
    recommendations: List[str]
    achievements: List[Dict[str, Any]]
    streak_info: Dict[str, Any]
    subject_breakdown: Dict[str, Any]
    learning_insights: Dict[str, Any]

class AdminDashboard(BaseModel):
    date_range: AnalyticsDateRange
    system_health: Dict[str, Any]
    user_statistics: Dict[str, Any]
    content_statistics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    error_logs: List[Dict[str, Any]]
    ai_service_status: Dict[str, Any]
    popular_content: List[Dict[str, Any]]
    user_feedback: Dict[str, Any]

# Report Schemas
class AnalyticsReport(BaseModel):
    report_id: str
    title: str
    description: Optional[str] = None
    report_type: str  # user_progress, system_performance, content_analytics
    date_range: AnalyticsDateRange
    filters: Dict[str, Any] = {}
    data: Dict[str, Any]
    charts: List[Dict[str, Any]] = []
    summary: Dict[str, Any]
    recommendations: List[str] = []
    generated_at: datetime
    generated_by: Optional[int] = None

class ReportRequest(BaseModel):
    report_type: str
    title: str
    description: Optional[str] = None
    date_range: AnalyticsDateRange
    filters: Dict[str, Any] = {}
    include_charts: bool = True
    include_raw_data: bool = False
    format: str = Field(default="json")  # json, csv, pdf

    @validator('report_type')
    def validate_report_type(cls, v):
        valid_types = ['user_progress', 'system_performance', 'content_analytics', 'learning_patterns', 'engagement']
        if v not in valid_types:
            raise ValueError(f'Report type must be one of: {valid_types}')
        return v

    @validator('format')
    def validate_format(cls, v):
        valid_formats = ['json', 'csv', 'pdf', 'excel']
        if v not in valid_formats:
            raise ValueError(f'Report format must be one of: {valid_formats}')
        return v

# Export Schemas
class DataExport(BaseModel):
    export_id: str
    export_type: str
    filters: Dict[str, Any]
    format: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    status: str = "pending"  # pending, processing, completed, failed
    progress: int = Field(default=0, ge=0, le=100)
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class ExportRequest(BaseModel):
    export_type: str
    filters: Dict[str, Any] = {}
    format: str = Field(default="csv")
    include_headers: bool = True
    date_range: Optional[AnalyticsDateRange] = None

    @validator('export_type')
    def validate_export_type(cls, v):
        valid_types = ['user_data', 'analytics', 'questions', 'sessions', 'events']
        if v not in valid_types:
            raise ValueError(f'Export type must be one of: {valid_types}')
        return v

# Additional Analytics Repository Schemas
class DailyUserActivityBase(BaseModel):
    user_id: int
    date: date
    questions_attempted: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    study_time_minutes: int = 0
    sessions_completed: int = 0
    accuracy_rate: float = 0.0

class DailyUserActivityCreate(DailyUserActivityBase):
    pass

class DailyUserActivityUpdate(BaseModel):
    questions_attempted: Optional[int] = None
    correct_answers: Optional[int] = None
    incorrect_answers: Optional[int] = None
    study_time_minutes: Optional[int] = None
    sessions_completed: Optional[int] = None
    accuracy_rate: Optional[float] = None

class DailyUserActivityRead(DailyUserActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WeeklyUserActivityBase(BaseModel):
    user_id: int
    year: int
    week_number: int
    questions_attempted: int = 0
    correct_answers: int = 0
    study_time_minutes: int = 0
    sessions_completed: int = 0
    accuracy_rate: float = 0.0

class WeeklyUserActivityCreate(WeeklyUserActivityBase):
    pass

class WeeklyUserActivityUpdate(BaseModel):
    questions_attempted: Optional[int] = None
    correct_answers: Optional[int] = None
    study_time_minutes: Optional[int] = None
    sessions_completed: Optional[int] = None
    accuracy_rate: Optional[float] = None

class WeeklyUserActivityRead(WeeklyUserActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MonthlyUserActivityBase(BaseModel):
    user_id: int
    year: int
    month: int
    questions_attempted: int = 0
    correct_answers: int = 0
    study_time_minutes: int = 0
    sessions_completed: int = 0
    accuracy_rate: float = 0.0

class MonthlyUserActivityCreate(MonthlyUserActivityBase):
    pass

class MonthlyUserActivityUpdate(BaseModel):
    questions_attempted: Optional[int] = None
    correct_answers: Optional[int] = None
    study_time_minutes: Optional[int] = None
    sessions_completed: Optional[int] = None
    accuracy_rate: Optional[float] = None

class MonthlyUserActivityRead(MonthlyUserActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SubjectPerformanceAnalyticsBase(BaseModel):
    user_id: int
    subject_id: int
    total_attempts: int = 0
    correct_attempts: int = 0
    accuracy_rate: float = 0.0
    average_time_per_question: float = 0.0
    improvement_rate: float = 0.0

class SubjectPerformanceAnalyticsCreate(SubjectPerformanceAnalyticsBase):
    pass

class SubjectPerformanceAnalyticsUpdate(BaseModel):
    total_attempts: Optional[int] = None
    correct_attempts: Optional[int] = None
    accuracy_rate: Optional[float] = None
    average_time_per_question: Optional[float] = None
    improvement_rate: Optional[float] = None

class SubjectPerformanceAnalyticsRead(SubjectPerformanceAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TopicPerformanceAnalyticsBase(BaseModel):
    user_id: int
    topic_id: int
    total_attempts: int = 0
    correct_attempts: int = 0
    accuracy_rate: float = 0.0
    average_time_per_question: float = 0.0
    improvement_rate: float = 0.0

class TopicPerformanceAnalyticsCreate(TopicPerformanceAnalyticsBase):
    pass

class TopicPerformanceAnalyticsUpdate(BaseModel):
    total_attempts: Optional[int] = None
    correct_attempts: Optional[int] = None
    accuracy_rate: Optional[float] = None
    average_time_per_question: Optional[float] = None
    improvement_rate: Optional[float] = None

class TopicPerformanceAnalyticsRead(TopicPerformanceAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DifficultyLevelAnalyticsBase(BaseModel):
    user_id: int
    difficulty_level: str
    total_attempts: int = 0
    correct_attempts: int = 0
    accuracy_rate: float = 0.0
    average_time_per_question: float = 0.0

class DifficultyLevelAnalyticsCreate(DifficultyLevelAnalyticsBase):
    pass

class DifficultyLevelAnalyticsUpdate(BaseModel):
    total_attempts: Optional[int] = None
    correct_attempts: Optional[int] = None
    accuracy_rate: Optional[float] = None
    average_time_per_question: Optional[float] = None

class DifficultyLevelAnalyticsRead(DifficultyLevelAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LearningPathAnalyticsBase(BaseModel):
    user_id: int
    path_name: str
    is_completed: bool = False
    progress_percentage: float = 0.0
    estimated_completion_time: Optional[int] = None

class LearningPathAnalyticsCreate(LearningPathAnalyticsBase):
    pass

class LearningPathAnalyticsUpdate(BaseModel):
    is_completed: Optional[bool] = None
    progress_percentage: Optional[float] = None
    estimated_completion_time: Optional[int] = None

class LearningPathAnalyticsRead(LearningPathAnalyticsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard and Report Schemas
class DashboardQuery(BaseModel):
    user_id: Optional[int] = None
    days_back: int = Field(default=7, ge=1, le=365)

class ReportQuery(BaseModel):
    report_type: str = Field(..., description="Type of report to generate")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None

class AnalyticsExport(BaseModel):
    export_type: str = Field(..., description="Export format: csv, json, pdf")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_raw_data: bool = False
