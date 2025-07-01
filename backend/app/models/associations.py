from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Boolean
from app.models.base import Base

# User-Subject associations (many-to-many)
user_subjects = Table(
    'user_subjects',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True),
    Column('enrolled_at', DateTime, nullable=True),
    Column('is_active', Boolean, default=True)
)

# User-Topic associations for tracking interest
user_topic_interests = Table(
    'user_topic_interests',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id'), primary_key=True),
    Column('interest_level', Integer, default=5),  # 1-10 scale
    Column('added_at', DateTime, nullable=True)
)

# Question-Tag associations (many-to-many)
question_tags = Table(
    'question_tags',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('tag_name', String(100), primary_key=True),
    Column('weight', Integer, default=1)  # Tag importance weight
)

# User study groups (many-to-many)
user_study_groups = Table(
    'user_study_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('study_groups.id'), primary_key=True),
    Column('role', String(50), default='member'),  # member, admin, moderator
    Column('joined_at', DateTime, nullable=True),
    Column('is_active', Boolean, default=True)
)

# Study group model
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class StudyGroup(Base):
    __tablename__ = "study_groups"

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Group settings
    is_public = Column(Boolean, default=False)
    max_members = Column(Integer, default=50)
    requires_approval = Column(Boolean, default=True)
    
    # Academic focus
    subject_ids = Column(JSON, default=list)  # List of subject IDs
    academic_level = Column(String(50), nullable=True)
    university = Column(String(200), nullable=True)
    
    # Activity
    member_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("User", secondary=user_study_groups, back_populates="study_groups")

    def __repr__(self):
        return f"<StudyGroup(id={self.id}, name='{self.name}', members={self.member_count})>"
