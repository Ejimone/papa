from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime

class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Relations
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(Integer, nullable=True)  # Will be ForeignKey when topics table is created
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_errors = Column(Text, nullable=True)
    
    # Content metadata
    material_type = Column(String(100), default="lecture_notes")
    tags = Column(JSON, nullable=True)
    content_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid conflict
    
    # RAG and AI features
    enable_rag = Column(Boolean, default=True)
    auto_extract_questions = Column(Boolean, default=False)
    questions_extracted = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="course_materials")
    uploader = relationship("User", back_populates="uploaded_materials")
    
    def __repr__(self):
        return f"<CourseMaterial(id={self.id}, title='{self.title}', file_type='{self.file_type}')>"

# Update the Subject model to include course_materials relationship
# This would be added to the Subject model in subject.py:
# course_materials = relationship("CourseMaterial", back_populates="subject")

# Update the User model to include uploaded_materials relationship  
# This would be added to the User model in user.py:
# uploaded_materials = relationship("CourseMaterial", back_populates="uploader")
