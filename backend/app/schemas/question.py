from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import BaseSchema
from app.models.question import QuestionType, DifficultyLevel

# Question Schemas
class QuestionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    answer: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    points: int = Field(default=1, ge=1, le=100)
    time_limit: Optional[int] = Field(None, ge=1)  # seconds
    subject_id: int
    topic_id: Optional[int] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    answer: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    question_type: Optional[QuestionType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    points: Optional[int] = Field(None, ge=1, le=100)
    time_limit: Optional[int] = Field(None, ge=1)
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class QuestionRead(BaseSchema):
    title: str
    content: str
    answer: Optional[str]
    options: Optional[Dict[str, Any]]
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    points: int
    time_limit: Optional[int]
    subject_id: int
    topic_id: Optional[int]
    created_by: Optional[int]
    is_active: bool
    is_verified: bool
    priority_score: float
    frequency_score: float
    is_processed_for_embedding: bool
    vector_id: Optional[str]

class QuestionResponse(QuestionRead):
    """Response schema for questions with additional metadata"""
    pass

class QuestionPublic(BaseModel):
    """Public view of question (without answer for practice mode)"""
    id: int
    title: str
    content: str
    options: Optional[Dict[str, Any]]
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    points: int
    time_limit: Optional[int]
    subject_id: int
    topic_id: Optional[int]
    created_at: datetime

class QuestionWithDetails(QuestionRead):
    """Question with related data"""
    subject: Optional[Dict[str, Any]] = None
    topic: Optional[Dict[str, Any]] = None
    question_metadata: Optional[Dict[str, Any]] = None
    images: List[Dict[str, Any]] = []
    explanations: List[Dict[str, Any]] = []
    hints: List[Dict[str, Any]] = []

# Question Metadata Schemas
class QuestionMetadataBase(BaseModel):
    tags: List[str] = []
    keywords: List[str] = []
    source: Optional[str] = None
    year: Optional[int] = Field(None, ge=1900, le=2100)
    semester: Optional[str] = None
    institution: Optional[str] = None
    exam_type: Optional[str] = None
    concepts: List[str] = []
    prerequisites: List[str] = []
    learning_objectives: List[str] = []

class QuestionMetadataCreate(QuestionMetadataBase):
    question_id: int

class QuestionMetadataUpdate(BaseModel):
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    source: Optional[str] = None
    year: Optional[int] = Field(None, ge=1900, le=2100)
    semester: Optional[str] = None
    institution: Optional[str] = None
    exam_type: Optional[str] = None
    concepts: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None

class QuestionMetadataRead(BaseSchema):
    question_id: int
    tags: List[str]
    keywords: List[str]
    source: Optional[str]
    year: Optional[int]
    semester: Optional[str]
    institution: Optional[str]
    exam_type: Optional[str]
    concepts: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    clarity_score: float
    completeness_score: float
    difficulty_confidence: float

# Question Image Schemas
class QuestionImageBase(BaseModel):
    image_url: str
    image_path: Optional[str] = None
    image_type: Optional[str] = None
    alt_text: Optional[str] = None

class QuestionImageCreate(QuestionImageBase):
    question_id: int

class QuestionImageUpdate(BaseModel):
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    image_type: Optional[str] = None
    alt_text: Optional[str] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class QuestionImageRead(BaseSchema):
    question_id: int
    image_url: str
    image_path: Optional[str]
    image_type: Optional[str]
    ocr_text: Optional[str]
    ocr_confidence: Optional[float]
    alt_text: Optional[str]
    width: Optional[int]
    height: Optional[int]
    file_size: Optional[int]
    is_processed: bool
    processed_at: Optional[datetime]

# Explanation Schemas
class ExplanationBase(BaseModel):
    content: str = Field(..., min_length=1)
    explanation_type: str = "step_by_step"
    approach: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None

class ExplanationCreate(ExplanationBase):
    question_id: int

class ExplanationUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    explanation_type: Optional[str] = None
    approach: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    is_verified: Optional[bool] = None

class ExplanationRead(BaseSchema):
    question_id: int
    content: str
    explanation_type: str
    approach: Optional[str]
    difficulty_level: Optional[DifficultyLevel]
    is_ai_generated: bool
    ai_model: Optional[str]
    confidence_score: Optional[float]
    is_verified: bool
    verified_by: Optional[int]
    verified_at: Optional[datetime]
    helpful_votes: int
    total_votes: int

# Hint Schemas
class HintBase(BaseModel):
    content: str = Field(..., min_length=1)
    level: int = Field(..., ge=1, le=10)
    hint_type: str = "concept"

class HintCreate(HintBase):
    question_id: int

class HintUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    level: Optional[int] = Field(None, ge=1, le=10)
    hint_type: Optional[str] = None

class HintRead(BaseSchema):
    question_id: int
    level: int
    content: str
    hint_type: str
    is_ai_generated: bool
    ai_model: Optional[str]
    usage_count: int
    effectiveness_score: float

# Similar Question Schemas
class SimilarQuestionBase(BaseModel):
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    similarity_type: str = "content"

class SimilarQuestionCreate(SimilarQuestionBase):
    original_question_id: int
    similar_question_id: int

class SimilarQuestionRead(BaseSchema):
    original_question_id: int
    similar_question_id: int
    similarity_score: float
    similarity_type: str
    algorithm_used: Optional[str]
    calculated_at: Optional[datetime]
    is_verified: bool

# Search and Filter Schemas
class QuestionFilter(BaseModel):
    subject_ids: Optional[List[int]] = None
    topic_ids: Optional[List[int]] = None
    question_types: Optional[List[QuestionType]] = None
    difficulty_levels: Optional[List[DifficultyLevel]] = None
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    year: Optional[int] = None
    semester: Optional[str] = None
    institution: Optional[str] = None
    exam_type: Optional[str] = None
    is_verified: Optional[bool] = None
    has_explanation: Optional[bool] = None
    has_hints: Optional[bool] = None
    min_priority_score: Optional[float] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class QuestionSearch(BaseModel):
    query: str = Field(..., min_length=1)
    filters: Optional[QuestionFilter] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_similar: bool = False
    semantic_search: bool = True

class QuestionSearchResult(BaseModel):
    questions: List[QuestionRead]
    total_count: int
    search_time_ms: float
    suggestions: Optional[List[str]] = None

# Bulk Operations
class QuestionBulkCreate(BaseModel):
    questions: List[QuestionCreate]

class QuestionSearchResponse(BaseModel):
    questions: List[QuestionRead]
    total_count: int
    query: str
    filters_applied: Dict[str, Any] = {}
    suggestions: List[str] = []
    search_time_ms: float = 0.0
    page: int = 1
    total_pages: int = 1
    skip_validation: bool = False
    batch_size: int = Field(default=100, ge=1, le=1000)

class QuestionBulkUpdate(BaseModel):
    question_ids: List[int]
    updates: QuestionUpdate
    skip_validation: bool = False

class QuestionBulkResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]] = []
    created_ids: Optional[List[int]] = None
    updated_ids: Optional[List[int]] = None

# Statistics and Analytics
class QuestionStats(BaseModel):
    total_questions: int
    by_subject: Dict[str, int]
    by_topic: Dict[str, int]
    by_difficulty: Dict[str, int]
    by_type: Dict[str, int]
    verified_percentage: float
    with_explanations: int
    with_hints: int
    with_images: int
    average_points: float
    average_time_limit: Optional[float]
