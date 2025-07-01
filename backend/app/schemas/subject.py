from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import BaseSchema

# Subject Schemas
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    department: Optional[str] = Field(None, max_length=200)
    level: Optional[int] = Field(None, ge=100, le=900)
    credits: Optional[int] = Field(None, ge=1, le=10)
    academic_year: Optional[str] = Field(None, max_length=20)
    semester: Optional[str] = Field(None, max_length=20)
    instructor: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: List[str] = []
    prerequisites: List[str] = []

    @validator('code')
    def validate_code(cls, v):
        if v and not v.replace(' ', '').replace('-', '').isalnum():
            raise ValueError('Subject code must contain only alphanumeric characters, spaces, and hyphens')
        return v

    @validator('academic_year')
    def validate_academic_year(cls, v):
        if v and not (len(v.split('-')) == 2 and all(part.isdigit() and len(part) == 4 for part in v.split('-'))):
            raise ValueError('Academic year must be in format YYYY-YYYY (e.g., 2023-2024)')
        return v

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    department: Optional[str] = Field(None, max_length=200)
    level: Optional[int] = Field(None, ge=100, le=900)
    credits: Optional[int] = Field(None, ge=1, le=10)
    academic_year: Optional[str] = Field(None, max_length=20)
    semester: Optional[str] = Field(None, max_length=20)
    instructor: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_popular: Optional[bool] = None

class SubjectRead(BaseSchema):
    name: str
    code: Optional[str]
    description: Optional[str]
    department: Optional[str]
    level: Optional[int]
    credits: Optional[int]
    academic_year: Optional[str]
    semester: Optional[str]
    instructor: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    tags: List[str]
    prerequisites: List[str]
    is_active: bool
    is_popular: bool
    total_questions: int
    total_students: int
    difficulty_average: int

class SubjectWithStats(SubjectRead):
    """Subject with additional statistics"""
    question_count_by_type: Dict[str, int] = {}
    question_count_by_difficulty: Dict[str, int] = {}
    average_completion_rate: float = 0.0
    enrolled_users_count: int = 0
    active_users_count: int = 0
    recent_activity_count: int = 0

class SubjectWithTopics(SubjectRead):
    """Subject with its topics"""
    topics: List[Dict[str, Any]] = []

# Topic Schemas
class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    subject_id: int
    parent_topic_id: Optional[int] = None
    level: int = Field(default=1, ge=1, le=10)
    order_index: int = Field(default=0, ge=0)
    learning_objectives: List[str] = []
    key_concepts: List[str] = []
    difficulty_level: str = Field(default="intermediate")
    estimated_study_time: Optional[int] = Field(None, ge=1)  # minutes
    tags: List[str] = []
    keywords: List[str] = []

    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_levels:
            raise ValueError(f'Difficulty level must be one of: {valid_levels}')
        return v

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject_id: Optional[int] = None
    parent_topic_id: Optional[int] = None
    level: Optional[int] = Field(None, ge=1, le=10)
    order_index: Optional[int] = Field(None, ge=0)
    learning_objectives: Optional[List[str]] = None
    key_concepts: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    estimated_study_time: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None

class TopicRead(BaseSchema):
    name: str
    description: Optional[str]
    subject_id: int
    parent_topic_id: Optional[int]
    level: int
    order_index: int
    learning_objectives: List[str]
    key_concepts: List[str]
    difficulty_level: str
    estimated_study_time: Optional[int]
    tags: List[str]
    keywords: List[str]
    is_active: bool
    total_questions: int
    completion_rate: int

class TopicWithSubtopics(TopicRead):
    """Topic with its subtopics"""
    subtopics: List["TopicRead"] = []
    full_path: str = ""

class TopicTree(BaseModel):
    """Hierarchical topic structure"""
    topic: TopicRead
    children: List["TopicTree"] = []
    question_count: int = 0
    total_question_count: int = 0  # Including subtopics

# Subject-Topic relationships
class SubjectTopicSummary(BaseModel):
    subject: SubjectRead
    topic_count: int
    total_questions: int
    completion_percentage: float
    difficulty_distribution: Dict[str, int]
    last_activity: Optional[datetime]

# Search and Filter Schemas
class SubjectFilter(BaseModel):
    departments: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    levels: Optional[List[int]] = None
    academic_years: Optional[List[str]] = None
    semesters: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    has_questions: Optional[bool] = None
    is_active: Optional[bool] = None
    is_popular: Optional[bool] = None
    min_credits: Optional[int] = None
    max_credits: Optional[int] = None

class TopicFilter(BaseModel):
    subject_ids: Optional[List[int]] = None
    parent_topic_ids: Optional[List[int]] = None
    difficulty_levels: Optional[List[str]] = None
    levels: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    has_questions: Optional[bool] = None
    is_active: Optional[bool] = None
    min_study_time: Optional[int] = None
    max_study_time: Optional[int] = None

class SubjectSearch(BaseModel):
    query: Optional[str] = None
    filters: Optional[SubjectFilter] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="name")
    sort_order: str = Field(default="asc")

    @validator('sort_by')
    def validate_sort_by(cls, v):
        valid_fields = ['name', 'code', 'level', 'credits', 'total_questions', 'created_at']
        if v not in valid_fields:
            raise ValueError(f'Sort field must be one of: {valid_fields}')
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v

class TopicSearch(BaseModel):
    query: Optional[str] = None
    filters: Optional[TopicFilter] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_subtopics: bool = False
    sort_by: str = Field(default="name")
    sort_order: str = Field(default="asc")

# Bulk Operations
class SubjectBulkCreate(BaseModel):
    subjects: List[SubjectCreate]
    skip_validation: bool = False

class TopicBulkCreate(BaseModel):
    topics: List[TopicCreate]
    skip_validation: bool = False

class SubjectBulkResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]] = []
    created_ids: Optional[List[int]] = None

class TopicBulkResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]] = []
    created_ids: Optional[List[int]] = None

# Statistics
class SubjectStats(BaseModel):
    total_subjects: int
    by_department: Dict[str, int]
    by_category: Dict[str, int]
    by_level: Dict[str, int]
    active_subjects: int
    popular_subjects: int
    total_questions: int
    total_enrolled_users: int

class TopicStats(BaseModel):
    total_topics: int
    by_subject: Dict[str, int]
    by_difficulty: Dict[str, int]
    by_level: Dict[str, int]
    active_topics: int
    total_questions: int
    average_study_time: Optional[float]

# Update TopicWithSubtopics forward reference
TopicWithSubtopics.model_rebuild()
TopicTree.model_rebuild()

class TopicWithQuestionCount(TopicRead):
    question_count: int = 0
