from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Table, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base # Assuming Base has id, created_at, updated_at

# Association table for question_tags (Many-to-Many)
# Placeholder: Actual Tag model would be needed
# question_tags_table = Table(
#     "question_tags_association",
#     Base.metadata,
#     Column("question_id", Integer, ForeignKey("questions.id"), primary_key=True),
#     Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
# )

class Question(Base):
    __tablename__ = "questions"

    # Core fields from documentation
    title = Column(String(255), nullable=True) # Optional title
    content = Column(Text, nullable=False) # Main text content of the question
    question_type = Column(String(50), nullable=True) # MCQ, Short Answer, Essay, Numerical (from MetadataExtractor)

    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True) # Link to Subject model
    # subject = relationship("Subject", back_populates="questions") # Define in Subject model too

    difficulty_level_label = Column(String(50), nullable=True) # e.g., Easy, Medium, Hard (from MetadataExtractor)
    difficulty_level_score = Column(Float, nullable=True) # e.g., 0.0 to 1.0 (from MetadataExtractor)

    # Metadata from documentation (question_metadata table in original SQL schema)
    # These could be columns directly on the Question table or in a related JSONB/JSON column,
    # or a separate QuestionMetadata one-to-one table.
    # For simplicity in this conceptual model, let's add some directly or use JSON.

    source = Column(String(255), nullable=True) # e.g., "Exam 2021", "Textbook Chapter 5"
    year = Column(Integer, nullable=True) # Year of the exam/source
    priority_score = Column(Float, nullable=True) # Calculated score for importance/frequency

    # keywords = Column(JSON, nullable=True) # Store as list of strings: ["keyword1", "keyword2"] (from TextProcessor/MetadataExtractor)
    # tags = relationship("Tag", secondary=question_tags_table, back_populates="questions") # If using a Tag model

    # AI-Generated Content / Fields (Conceptual - not necessarily direct DB columns without thought)
    # ai_explanation_id = Column(Integer, ForeignKey("explanations.id"), nullable=True) # If explanations are separate
    # ai_explanation_text = Column(Text, nullable=True) # Or store directly if simple

    # raw_ocr_text = Column(Text, nullable=True) # If question originated from an image
    # image_url = Column(String, nullable=True) # If an image is associated

    # For vector storage, the actual embedding vector is usually NOT stored in PostgreSQL.
    # It's stored in a vector database like ChromaDB.
    # PostgreSQL would store the ID that links to the vector in ChromaDB.
    # vector_id = Column(String, unique=True, index=True, nullable=True) # ID used in ChromaDB

    # Fields for tracking processing status
    is_processed_for_embedding = Column(Boolean, default=False)
    processing_error_log = Column(Text, nullable=True)


    # Relationships (examples)
    # images = relationship("QuestionImage", back_populates="question") # If QuestionImage model exists
    # attempts = relationship("UserAttempt", back_populates="question") # If UserAttempt model exists
    # original_for_similars = relationship("SimilarQuestion", foreign_keys="[SimilarQuestion.similar_question_id]", back_populates="similar_question_obj")
    # similars_generated = relationship("SimilarQuestion", foreign_keys="[SimilarQuestion.original_question_id]", back_populates="original_question_obj")


    def __repr__(self):
        return f"<Question(id={self.id}, title='{self.title[:30]}...')>"


# Example for related models if defined (conceptual)
# class Subject(Base):
#     __tablename__ = "subjects"
#     name = Column(String, unique=True, index=True)
#     questions = relationship("Question", back_populates="subject")

# class Tag(Base):
#     __tablename__ = "tags"
#     name = Column(String, unique=True, index=True)
#     questions = relationship("Question", secondary=question_tags_table, back_populates="tags")

# class QuestionImage(Base):
#     __tablename__ = "question_images"
#     question_id = Column(Integer, ForeignKey("questions.id"))
#     image_url = Column(String, nullable=False)
#     ocr_text = Column(Text, nullable=True)
#     question = relationship("Question", back_populates="images")

# class Explanation(Base):
# __tablename__ = "explanations"
#    question_id = Column(Integer, ForeignKey("questions.id"), unique=True) # One-to-one or one-to-many if multiple explanation types
#    content = Column(Text, nullable=False)
#    type = Column(String(50), default="ai_generated") # e.g., "ai_generated", "manual"
#    # question = relationship("Question", back_populates="explanation")

# class SimilarQuestion(Base): # Association object for self-referential many-to-many
#     __tablename__ = "similar_questions"
#     original_question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
#     similar_question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
#     similarity_score = Column(Float, nullable=True)
#
#     original_question_obj = relationship("Question", foreign_keys=[original_question_id], back_populates="similars_generated")
#     similar_question_obj = relationship("Question", foreign_keys=[similar_question_id], back_populates="original_for_similars")

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
