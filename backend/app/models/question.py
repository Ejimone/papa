from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import uuid
import enum

class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    NUMERICAL = "numerical"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"

class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Question(Base):
    __tablename__ = "questions"

    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)  # Correct answer
    options = Column(JSON, nullable=True)  # For multiple choice questions
    question_type = Column(Enum(QuestionType), nullable=False, default=QuestionType.MULTIPLE_CHOICE)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False, default=DifficultyLevel.INTERMEDIATE)
    points = Column(Integer, default=1)
    time_limit = Column(Integer, nullable=True)  # Time limit in seconds
    
    # Foreign Keys
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Status and Quality
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    priority_score = Column(Float, default=0.0)  # AI-calculated priority
    frequency_score = Column(Float, default=0.0)  # How often it appears in exams
    
    # Relationships
    subject = relationship("Subject", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    creator = relationship("User", foreign_keys=[created_by])
    metadata = relationship("QuestionMetadata", back_populates="question", uselist=False, cascade="all, delete-orphan")
    images = relationship("QuestionImage", back_populates="question", cascade="all, delete-orphan")
    explanations = relationship("Explanation", back_populates="question", cascade="all, delete-orphan")
    hints = relationship("Hint", back_populates="question", cascade="all, delete-orphan")
    user_attempts = relationship("UserAttempt", back_populates="question")
    bookmarks = relationship("UserBookmark", back_populates="question")
    
    # Similar questions relationships
    similar_to = relationship(
        "SimilarQuestion",
        foreign_keys="SimilarQuestion.original_question_id",
        back_populates="original_question"
    )
    similar_from = relationship(
        "SimilarQuestion", 
        foreign_keys="SimilarQuestion.similar_question_id",
        back_populates="similar_question"
    )

    def __repr__(self):
        return f"<Question(id={self.id}, title='{self.title[:50]}...', type='{self.question_type}')>"

class QuestionMetadata(Base):
    __tablename__ = "question_metadata"

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, unique=True, index=True)
    tags = Column(JSON, default=list)  # List of tags
    keywords = Column(JSON, default=list)  # AI-extracted keywords
    source = Column(String(200), nullable=True)  # Source exam/book
    year = Column(Integer, nullable=True)  # Year of exam
    semester = Column(String(50), nullable=True)  # e.g., "Fall 2023"
    institution = Column(String(200), nullable=True)  # University/Institution
    exam_type = Column(String(100), nullable=True)  # Midterm, Final, Quiz, etc.
    
    # AI-generated metadata
    concepts = Column(JSON, default=list)  # Key concepts covered
    prerequisites = Column(JSON, default=list)  # Required knowledge
    learning_objectives = Column(JSON, default=list)  # What this question tests
    
    # Quality metrics
    clarity_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    difficulty_confidence = Column(Float, default=0.0)
    
    # Relationships
    question = relationship("Question", back_populates="metadata")

    def __repr__(self):
        return f"<QuestionMetadata(question_id={self.question_id}, source='{self.source}')>"

class QuestionImage(Base):
    __tablename__ = "question_images"

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    image_path = Column(String(500), nullable=True)  # Local storage path
    image_type = Column(String(50), nullable=True)  # question_image, diagram, chart, etc.
    ocr_text = Column(Text, nullable=True)  # Extracted text from image
    ocr_confidence = Column(Float, nullable=True)  # OCR confidence score
    alt_text = Column(Text, nullable=True)  # Alternative text for accessibility
    
    # Image properties
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    question = relationship("Question", back_populates="images")

    def __repr__(self):
        return f"<QuestionImage(id={self.id}, question_id={self.question_id}, type='{self.image_type}')>"

class Explanation(Base):
    __tablename__ = "explanations"

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    explanation_type = Column(String(50), default="step_by_step")  # step_by_step, conceptual, alternative
    approach = Column(String(100), nullable=True)  # Method/approach used
    difficulty_level = Column(Enum(DifficultyLevel), nullable=True)
    
    # AI generation info
    is_ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)  # Which AI model generated this
    generation_prompt = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Quality and validation
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # User feedback
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Relationships
    question = relationship("Question", back_populates="explanations")
    verifier = relationship("User", foreign_keys=[verified_by])

    def __repr__(self):
        return f"<Explanation(id={self.id}, question_id={self.question_id}, type='{self.explanation_type}')>"

class Hint(Base):
    __tablename__ = "hints"

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    level = Column(Integer, nullable=False, default=1)  # Progressive hint levels
    content = Column(Text, nullable=False)
    hint_type = Column(String(50), default="concept")  # concept, method, direction, formula
    
    # AI generation info
    is_ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.0)  # How helpful users find this hint
    
    # Relationships
    question = relationship("Question", back_populates="hints")

    def __repr__(self):
        return f"<Hint(id={self.id}, question_id={self.question_id}, level={self.level})>"

class SimilarQuestion(Base):
    __tablename__ = "similar_questions"

    original_question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    similar_question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    similarity_type = Column(String(50), default="content")  # content, concept, difficulty, format
    
    # AI calculation info
    algorithm_used = Column(String(100), nullable=True)  # embedding, semantic, etc.
    calculated_at = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    original_question = relationship("Question", foreign_keys=[original_question_id], back_populates="similar_to")
    similar_question = relationship("Question", foreign_keys=[similar_question_id], back_populates="similar_from")

    def __repr__(self):
        return f"<SimilarQuestion(original={self.original_question_id}, similar={self.similar_question_id}, score={self.similarity_score})>"
