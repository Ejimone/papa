from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.subject import Subject, Topic
from app.models.user import User
from app.schemas.subject import (
    SubjectCreate, SubjectRead, SubjectUpdate,
    TopicCreate, TopicRead, TopicUpdate,
    SubjectWithTopics, TopicWithQuestionCount
)
from app.api.deps import get_current_user, get_current_active_user
from app.services.base import BaseService

router = APIRouter()

# Subject endpoints
@router.get("/", response_model=List[SubjectRead])
async def get_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all subjects"""
    try:
        query = select(Subject).offset(skip).limit(limit).order_by(Subject.name)
        result = await db.execute(query)
        subjects = result.scalars().all()
        return subjects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/with-topics", response_model=List[SubjectWithTopics])
async def get_subjects_with_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get subjects with their topics"""
    try:
        query = select(Subject).options(
            selectinload(Subject.topics)
        ).offset(skip).limit(limit).order_by(Subject.name)
        
        result = await db.execute(query)
        subjects = result.scalars().all()
        return subjects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{subject_id}", response_model=SubjectRead)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific subject by ID"""
    try:
        query = select(Subject).where(Subject.id == subject_id)
        result = await db.execute(query)
        subject = result.scalar_one_or_none()
        
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        return subject
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{subject_id}/with-topics", response_model=SubjectWithTopics)
async def get_subject_with_topics(
    subject_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a subject with its topics"""
    try:
        query = select(Subject).options(
            selectinload(Subject.topics)
        ).where(Subject.id == subject_id)
        
        result = await db.execute(query)
        subject = result.scalar_one_or_none()
        
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        return subject
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=SubjectRead)
async def create_subject(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new subject (admin only)"""
    try:
        # Check if user has admin privileges (you might want to implement role-based access)
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if subject with this name already exists
        existing_query = select(Subject).where(Subject.name == subject_data.name)
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="Subject with this name already exists")
        
        # Create new subject
        subject = Subject(**subject_data.dict())
        db.add(subject)
        await db.commit()
        await db.refresh(subject)
        
        return subject
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{subject_id}", response_model=SubjectRead)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a subject (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get existing subject
        query = select(Subject).where(Subject.id == subject_id)
        result = await db.execute(query)
        subject = result.scalar_one_or_none()
        
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # Update subject
        update_data = subject_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subject, field, value)
        
        await db.commit()
        await db.refresh(subject)
        
        return subject
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a subject (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get existing subject
        query = select(Subject).where(Subject.id == subject_id)
        result = await db.execute(query)
        subject = result.scalar_one_or_none()
        
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # Delete subject
        await db.delete(subject)
        await db.commit()
        
        return {"message": "Subject deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Topic endpoints
@router.get("/{subject_id}/topics", response_model=List[TopicRead])
async def get_topics_by_subject(
    subject_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all topics for a subject"""
    try:
        query = select(Topic).where(
            Topic.subject_id == subject_id
        ).offset(skip).limit(limit).order_by(Topic.name)
        
        result = await db.execute(query)
        topics = result.scalars().all()
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{subject_id}/topics/with-question-count", response_model=List[TopicWithQuestionCount])
async def get_topics_with_question_count(
    subject_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get topics with question count for a subject"""
    try:
        from app.models.question import Question
        
        # Get topics with question count
        query = select(
            Topic,
            func.count(Question.id).label('question_count')
        ).outerjoin(Question).where(
            Topic.subject_id == subject_id
        ).group_by(Topic.id).order_by(Topic.name)
        
        result = await db.execute(query)
        topics_with_count = []
        
        for topic, question_count in result:
            topic_dict = {
                "id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "subject_id": topic.subject_id,
                "created_at": topic.created_at,
                "updated_at": topic.updated_at,
                "question_count": question_count or 0
            }
            topics_with_count.append(topic_dict)
        
        return topics_with_count
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics/{topic_id}", response_model=TopicRead)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific topic by ID"""
    try:
        query = select(Topic).where(Topic.id == topic_id)
        result = await db.execute(query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return topic
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{subject_id}/topics", response_model=TopicRead)
async def create_topic(
    subject_id: int,
    topic_data: TopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new topic for a subject (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if subject exists
        subject_query = select(Subject).where(Subject.id == subject_id)
        subject_result = await db.execute(subject_query)
        subject = subject_result.scalar_one_or_none()
        
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # Check if topic with this name already exists in the subject
        existing_query = select(Topic).where(
            Topic.subject_id == subject_id,
            Topic.name == topic_data.name
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="Topic with this name already exists in this subject")
        
        # Create new topic
        topic_dict = topic_data.dict()
        topic_dict["subject_id"] = subject_id
        topic = Topic(**topic_dict)
        
        db.add(topic)
        await db.commit()
        await db.refresh(topic)
        
        return topic
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/topics/{topic_id}", response_model=TopicRead)
async def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a topic (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get existing topic
        query = select(Topic).where(Topic.id == topic_id)
        result = await db.execute(query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Update topic
        update_data = topic_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)
        
        await db.commit()
        await db.refresh(topic)
        
        return topic
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a topic (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get existing topic
        query = select(Topic).where(Topic.id == topic_id)
        result = await db.execute(query)
        topic = result.scalar_one_or_none()
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Delete topic
        await db.delete(topic)
        await db.commit()
        
        return {"message": "Topic deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[SubjectRead])
async def search_subjects(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Search subjects by name or description"""
    try:
        search_term = f"%{q}%"
        query = select(Subject).where(
            Subject.name.ilike(search_term) | 
            Subject.description.ilike(search_term)
        ).limit(limit).order_by(Subject.name)
        
        result = await db.execute(query)
        subjects = result.scalars().all()
        return subjects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics/search", response_model=List[TopicRead])
async def search_topics(
    q: str = Query(..., description="Search query"),
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Search topics by name or description"""
    try:
        search_term = f"%{q}%"
        query = select(Topic).where(
            Topic.name.ilike(search_term) | 
            Topic.description.ilike(search_term)
        )
        
        if subject_id:
            query = query.where(Topic.subject_id == subject_id)
        
        query = query.limit(limit).order_by(Topic.name)
        
        result = await db.execute(query)
        topics = result.scalars().all()
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
