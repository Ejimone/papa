from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime
import enum

class SessionType(str, enum.Enum):
    QUICK_PRACTICE = "quick_practice"
    TARGETED_STUDY = "targeted_study"
    MOCK_TEST = "mock_test"
    REVIEW_SESSION = "review_session"
    CHALLENGE_MODE = "challenge_mode"

class SessionStatus(str, enum.Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"

class AttemptStatus(str, enum.Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    SKIPPED = "skipped"
    FLAGGED = "flagged"

class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_type = Column(Enum(SessionType), nullable=False, default=SessionType.QUICK_PRACTICE)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.STARTED)
    
    # Session configuration
    title = Column(String(200), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    difficulty_level = Column(String(50), nullable=True)
    question_count = Column(Integer, default=10)
    time_limit = Column(Integer, nullable=True)  # Total time limit in seconds
    
    # Session filters
    filters = Column(JSON, default=dict)  # Store complex filtering criteria
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_time_spent = Column(Integer, default=0)  # Seconds
    
    # Results
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    skipped_questions = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    
    # Performance metrics
    average_time_per_question = Column(Float, nullable=True)
    fastest_answer_time = Column(Float, nullable=True)
    slowest_answer_time = Column(Float, nullable=True)
    
    # Learning insights
    strengths = Column(JSON, default=list)  # Topics/concepts user performed well in
    weaknesses = Column(JSON, default=list)  # Areas needing improvement
    recommendations = Column(JSON, default=list)  # AI-generated recommendations
    
    # Relationships
    user = relationship("User")
    subject = relationship("Subject")
    topic = relationship("Topic")
    attempts = relationship("UserAttempt", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PracticeSession(id={self.id}, user_id={self.user_id}, type='{self.session_type}', status='{self.status}')>"

class UserAttempt(Base):
    __tablename__ = "user_attempts"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=True, index=True)
    
    # Answer details
    user_answer = Column(Text, nullable=True)
    selected_options = Column(JSON, nullable=True)  # For multiple choice
    is_correct = Column(Boolean, nullable=True)
    status = Column(Enum(AttemptStatus), nullable=False, default=AttemptStatus.INCORRECT)
    
    # Timing
    time_taken = Column(Float, nullable=True)  # Seconds
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    
    # Learning assistance used
    hints_used = Column(Integer, default=0)
    explanation_viewed = Column(Boolean, default=False)
    flagged_for_review = Column(Boolean, default=False)
    
    # Confidence and difficulty
    confidence_level = Column(Integer, nullable=True)  # 1-5 scale
    perceived_difficulty = Column(Integer, nullable=True)  # 1-5 scale
    
    # Performance tracking
    attempt_number = Column(Integer, default=1)  # Which attempt for this question
    improvement_score = Column(Float, nullable=True)  # Improvement from previous attempts
    
    # Metadata
    device_type = Column(String(50), nullable=True)  # mobile, tablet, desktop
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User")
    question = relationship("Question", back_populates="user_attempts")
    session = relationship("PracticeSession", back_populates="attempts")

    def __repr__(self):
        return f"<UserAttempt(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, correct={self.is_correct})>"

class UserBookmark(Base):
    __tablename__ = "user_bookmarks"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    
    # Bookmark organization
    bookmark_type = Column(String(50), default="general")  # review_later, difficult, favorite
    tags = Column(JSON, default=list)  # User-defined tags
    notes = Column(Text, nullable=True)  # User notes
    
    # Priority and planning
    priority = Column(Integer, default=1)  # 1-5 priority scale
    target_review_date = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_mastered = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")
    question = relationship("Question", back_populates="bookmarks")

    def __repr__(self):
        return f"<UserBookmark(user_id={self.user_id}, question_id={self.question_id}, type='{self.bookmark_type}')>"

class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    
    # Progress metrics
    total_questions_attempted = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    skipped_questions = Column(Integer, default=0)
    
    # Performance metrics
    accuracy_rate = Column(Float, default=0.0)  # Percentage
    average_time_per_question = Column(Float, nullable=True)
    improvement_rate = Column(Float, default=0.0)  # Rate of improvement over time
    consistency_score = Column(Float, default=0.0)  # How consistent performance is
    
    # Mastery tracking
    mastery_level = Column(Float, default=0.0)  # 0.0 to 1.0
    competency_score = Column(Float, default=0.0)  # Overall competency in subject/topic
    weak_areas = Column(JSON, default=list)  # Specific topics needing work
    strong_areas = Column(JSON, default=list)  # Areas of strength
    
    # Learning patterns
    preferred_difficulty = Column(String(50), nullable=True)
    learning_velocity = Column(Float, default=0.0)  # How quickly user learns
    retention_rate = Column(Float, default=0.0)  # How well user retains information
    
    # Activity tracking
    last_practiced_at = Column(DateTime, nullable=True)
    streak_days = Column(Integer, default=0)
    total_study_time = Column(Integer, default=0)  # Total time in seconds
    sessions_completed = Column(Integer, default=0)
    
    # Goals and targets
    target_accuracy = Column(Float, default=80.0)  # Target accuracy percentage
    daily_question_goal = Column(Integer, default=10)
    weekly_time_goal = Column(Integer, default=300)  # Minutes per week
    
    # AI-generated insights
    learning_style = Column(String(100), nullable=True)  # AI-determined learning style
    predicted_exam_score = Column(Float, nullable=True)  # AI prediction
    recommended_study_time = Column(Integer, nullable=True)  # Minutes per day
    next_review_topics = Column(JSON, default=list)  # AI-recommended topics to review
    
    # Relationships
    user = relationship("User")
    subject = relationship("Subject", back_populates="user_progress")
    topic = relationship("Topic")

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, subject_id={self.subject_id}, accuracy={self.accuracy_rate}%)>"
