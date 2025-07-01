from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base

class Subject(Base):
    __tablename__ = "subjects"

    name = Column(String(200), nullable=False, index=True)
    code = Column(String(20), nullable=True, unique=True, index=True)  # Course code like CS101
    description = Column(Text, nullable=True)
    department = Column(String(200), nullable=True)
    level = Column(Integer, nullable=True)  # 100, 200, 300, 400 level courses
    credits = Column(Integer, nullable=True)
    
    # Academic info
    academic_year = Column(String(20), nullable=True)  # 2023-2024
    semester = Column(String(20), nullable=True)  # Fall, Spring, Summer
    instructor = Column(String(200), nullable=True)
    
    # Organization
    category = Column(String(100), nullable=True)  # Mathematics, Science, Engineering, etc.
    subcategory = Column(String(100), nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)
    prerequisites = Column(JSON, default=list)  # List of prerequisite subject codes
    
    # Status
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    
    # Statistics (can be calculated periodically)
    total_questions = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    difficulty_average = Column(Integer, default=0)  # Average difficulty of questions
    
    # Relationships
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="subject")
    user_progress = relationship("UserProgress", back_populates="subject")
    enrolled_users = relationship("User", secondary="user_subjects", back_populates="subjects")

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', code='{self.code}')>"

class Topic(Base):
    __tablename__ = "topics"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    
    # Hierarchical structure
    parent_topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)
    level = Column(Integer, default=1)  # Depth in hierarchy
    order_index = Column(Integer, default=0)  # Order within parent topic
    
    # Educational metadata
    learning_objectives = Column(JSON, default=list)
    key_concepts = Column(JSON, default=list)
    difficulty_level = Column(String(20), default="intermediate")
    estimated_study_time = Column(Integer, nullable=True)  # Minutes
    
    # Content organization
    tags = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    
    # Status and metrics
    is_active = Column(Boolean, default=True)
    total_questions = Column(Integer, default=0)
    completion_rate = Column(Integer, default=0)  # Percentage of students who master this topic
    
    # Relationships
    subject = relationship("Subject", back_populates="topics")
    parent_topic = relationship("Topic", remote_side="Topic.id", back_populates="subtopics")
    subtopics = relationship("Topic", back_populates="parent_topic", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="topic")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', subject_id={self.subject_id})>"

    @property
    def full_path(self):
        """Get the full hierarchical path of the topic"""
        path = [self.name]
        current = self.parent_topic
        while current:
            path.insert(0, current.name)
            current = current.parent_topic
        return " > ".join(path)
