from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.question import (
    QuestionCreate, QuestionRead, QuestionUpdate, QuestionFilter, QuestionSearch,
    QuestionMetadataCreate, QuestionMetadataRead, QuestionMetadataUpdate,
    ExplanationCreate, ExplanationRead, HintCreate, HintRead,
    QuestionPublic, QuestionResponse, QuestionBulkCreate, QuestionSearchResponse
)
from app.api.deps import get_current_user, get_current_active_user
from app.services.question_service import QuestionService

router = APIRouter()

@router.get("/", response_model=List[QuestionRead])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    question_type: Optional[str] = Query(None, description="Filter by question type"),
    verified_only: bool = Query(False, description="Show only verified questions"),
    db: AsyncSession = Depends(get_db)
):
    """Get questions with optional filtering"""
    try:
        service = QuestionService(db)
        
        # Build filters
        filters = QuestionFilter(
            subject_ids=[subject_id] if subject_id else None,
            topic_ids=[topic_id] if topic_id else None,
            difficulty_levels=[difficulty] if difficulty else None,
            question_types=[question_type] if question_type else None,
            is_verified=verified_only if verified_only else None
        )
        
        questions = await service.get_filtered(filters, skip, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=QuestionSearchResponse)
async def search_questions(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    subject_ids: Optional[List[int]] = Query(None, description="Filter by subject IDs"),
    difficulty_levels: Optional[List[str]] = Query(None, description="Filter by difficulty levels"),
    verified_only: bool = Query(False, description="Show only verified questions"),
    db: AsyncSession = Depends(get_db)
):
    """Search questions with text search and filters"""
    try:
        service = QuestionService(db)
        
        # Build search parameters
        filters = QuestionFilter(
            subject_ids=subject_ids,
            difficulty_levels=difficulty_levels,
            is_verified=verified_only if verified_only else None
        )
        
        search_params = QuestionSearch(
            query=q,
            filters=filters,
            offset=skip,
            limit=limit
        )
        
        result = await service.search_questions(search_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    include_details: bool = Query(True, description="Include metadata, images, explanations, hints"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific question by ID"""
    try:
        service = QuestionService(db)
        
        if include_details:
            question = await service.get_with_details(question_id)
        else:
            question = await service.get(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{question_id}/public", response_model=QuestionPublic)
async def get_question_public(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get question in public format (without answer for practice mode)"""
    try:
        service = QuestionService(db)
        question = await service.get_with_details(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Convert to public format (without answer)
        return QuestionPublic(
            id=question.id,
            title=question.title,
            content=question.content,
            question_type=question.question_type,
            difficulty_level=question.difficulty_level,
            points=question.points,
            subject_id=question.subject_id,
            topic_id=question.topic_id,
            images=question.images or [],
            hints=question.hints or [],
            created_at=question.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=QuestionRead)
async def create_question(
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new question"""
    try:
        service = QuestionService(db)
        question = await service.create(question_data)
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=Dict[str, Any])
async def create_questions_bulk(
    questions_data: QuestionBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create multiple questions in bulk"""
    try:
        service = QuestionService(db)
        created_questions = []
        failed_questions = []
        
        for question_data in questions_data.questions:
            try:
                question = await service.create(question_data)
                created_questions.append(question)
            except Exception as e:
                failed_questions.append({
                    "question_data": question_data.dict(),
                    "error": str(e)
                })
        
        return {
            "created_count": len(created_questions),
            "failed_count": len(failed_questions),
            "created_questions": created_questions,
            "failed_questions": failed_questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a question"""
    try:
        service = QuestionService(db)
        question = await service.update(question_id, question_data)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a question"""
    try:
        service = QuestionService(db)
        success = await service.delete(question_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {"message": "Question deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subject/{subject_id}", response_model=List[QuestionRead])
async def get_questions_by_subject(
    subject_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get questions by subject"""
    try:
        service = QuestionService(db)
        questions = await service.get_by_subject(subject_id, skip, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic/{topic_id}", response_model=List[QuestionRead])
async def get_questions_by_topic(
    topic_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get questions by topic"""
    try:
        service = QuestionService(db)
        questions = await service.get_by_topic(topic_id, skip, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/random", response_model=List[QuestionPublic])
async def get_random_questions(
    count: int = Query(10, ge=1, le=50, description="Number of random questions"),
    subject_ids: Optional[List[int]] = Query(None, description="Filter by subject IDs"),
    difficulty_levels: Optional[List[str]] = Query(None, description="Filter by difficulty levels"),
    question_types: Optional[List[str]] = Query(None, description="Filter by question types"),
    db: AsyncSession = Depends(get_db)
):
    """Get random questions for practice"""
    try:
        service = QuestionService(db)
        
        filters = None
        if subject_ids or difficulty_levels or question_types:
            filters = QuestionFilter(
                subject_ids=subject_ids,
                difficulty_levels=difficulty_levels,
                question_types=question_types
            )
        
        questions = await service.get_random_questions(count, filters)
        
        # Convert to public format
        public_questions = []
        for question in questions:
            public_questions.append(QuestionPublic(
                id=question.id,
                title=question.title,
                content=question.content,
                question_type=question.question_type,
                difficulty_level=question.difficulty_level,
                points=question.points,
                subject_id=question.subject_id,
                topic_id=question.topic_id,
                images=question.images or [],
                hints=question.hints or [],
                created_at=question.created_at
            ))
        
        return public_questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{question_id}/similar", response_model=List[QuestionRead])
async def get_similar_questions(
    question_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get similar questions"""
    try:
        service = QuestionService(db)
        questions = await service.get_similar_questions(question_id, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Question metadata endpoints
@router.post("/{question_id}/metadata", response_model=QuestionMetadataRead)
async def add_question_metadata(
    question_id: int,
    metadata_data: QuestionMetadataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add metadata to a question"""
    try:
        service = QuestionService(db)
        metadata = await service.add_metadata(question_id, metadata_data)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Explanation endpoints
@router.post("/{question_id}/explanations", response_model=ExplanationRead)
async def add_explanation(
    question_id: int,
    explanation_data: ExplanationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add an explanation to a question"""
    try:
        service = QuestionService(db)
        explanation = await service.add_explanation(question_id, explanation_data)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Hint endpoints
@router.post("/{question_id}/hints", response_model=HintRead)
async def add_hint(
    question_id: int,
    hint_data: HintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a hint to a question"""
    try:
        service = QuestionService(db)
        hint = await service.add_hint(question_id, hint_data)
        return hint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_question_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get question statistics"""
    try:
        service = QuestionService(db)
        stats = await service.get_question_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
