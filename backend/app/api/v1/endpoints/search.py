from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.question import QuestionFilter
from app.api.deps import get_current_user, get_current_active_user
from app.services.search_service import SearchService

router = APIRouter()

@router.get("/questions", response_model=Dict[str, Any])
async def search_questions(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    subject_ids: Optional[List[int]] = Query(None, description="Filter by subject IDs"),
    topic_ids: Optional[List[int]] = Query(None, description="Filter by topic IDs"),
    difficulty_levels: Optional[List[str]] = Query(None, description="Filter by difficulty levels"),
    question_types: Optional[List[str]] = Query(None, description="Filter by question types"),
    verified_only: bool = Query(False, description="Show only verified questions"),
    min_points: Optional[int] = Query(None, description="Minimum points"),
    max_points: Optional[int] = Query(None, description="Maximum points"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Search questions with text search and filters"""
    try:
        service = SearchService(db)
        
        # Build filters
        filters = None
        if any([subject_ids, topic_ids, difficulty_levels, question_types, verified_only, min_points, max_points]):
            filters = QuestionFilter(
                subject_ids=subject_ids,
                topic_ids=topic_ids,
                difficulty_levels=difficulty_levels,
                question_types=question_types,
                is_verified=verified_only if verified_only else None,
                min_points=min_points,
                max_points=max_points
            )
        
        user_id = current_user.id if current_user else None
        result = await service.search_questions(q, filters, user_id, skip, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subjects-topics", response_model=Dict[str, Any])
async def search_subjects_and_topics(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search subjects and topics"""
    try:
        service = SearchService(db)
        result = await service.search_subjects_and_topics(q, skip, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookmarks", response_model=Dict[str, Any])
async def search_user_bookmarks(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Search user's bookmarks"""
    try:
        service = SearchService(db)
        result = await service.search_user_bookmarks(current_user.id, q, skip, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    q: str = Query(..., description="Partial search query"),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Get search suggestions based on partial query"""
    try:
        service = SearchService(db)
        suggestions = await service.get_search_suggestions(q, limit)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular", response_model=List[str])
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get popular search terms"""
    try:
        service = SearchService(db)
        popular_searches = await service.get_popular_searches(limit)
        return popular_searches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/advanced", response_model=Dict[str, Any])
async def advanced_search(
    search_params: Dict[str, Any],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Perform advanced search with multiple criteria"""
    try:
        service = SearchService(db)
        result = await service.advanced_search(search_params, skip, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters/options", response_model=Dict[str, Any])
async def get_search_filter_options(
    db: AsyncSession = Depends(get_db)
):
    """Get available filter options for search"""
    try:
        from app.models.subject import Subject, Topic
        from app.models.question import QuestionType, DifficultyLevel
        from sqlalchemy import select, func
        
        # Get subjects
        subjects_query = select(Subject.id, Subject.name).order_by(Subject.name)
        subjects_result = await db.execute(subjects_query)
        subjects = [{"id": row[0], "name": row[1]} for row in subjects_result]
        
        # Get topics
        topics_query = select(Topic.id, Topic.name, Topic.subject_id).order_by(Topic.name)
        topics_result = await db.execute(topics_query)
        topics = [{"id": row[0], "name": row[1], "subject_id": row[2]} for row in topics_result]
        
        # Get difficulty levels
        difficulty_levels = [level.value for level in DifficultyLevel]
        
        # Get question types
        question_types = [qtype.value for qtype in QuestionType]
        
        # Get point ranges (you might want to calculate this from actual data)
        point_ranges = [
            {"min": 1, "max": 5, "label": "1-5 points"},
            {"min": 6, "max": 10, "label": "6-10 points"},
            {"min": 11, "max": 15, "label": "11-15 points"},
            {"min": 16, "max": 20, "label": "16-20 points"},
        ]
        
        return {
            "subjects": subjects,
            "topics": topics,
            "difficulty_levels": difficulty_levels,
            "question_types": question_types,
            "point_ranges": point_ranges,
            "sort_options": [
                {"value": "relevance", "label": "Relevance"},
                {"value": "newest", "label": "Newest First"},
                {"value": "oldest", "label": "Oldest First"},
                {"value": "difficulty", "label": "Difficulty"},
                {"value": "points", "label": "Points (High to Low)"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/autocomplete", response_model=List[Dict[str, Any]])
async def search_autocomplete(
    q: str = Query(..., description="Search query for autocomplete"),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get autocomplete suggestions with categories"""
    try:
        from app.models.subject import Subject, Topic
        from app.models.question import Question
        from sqlalchemy import select
        
        search_term = f"%{q}%"
        suggestions = []
        
        # Search subjects
        subjects_query = select(Subject.id, Subject.name).where(
            Subject.name.ilike(search_term)
        ).limit(limit // 3)
        
        subjects_result = await db.execute(subjects_query)
        for subject_id, subject_name in subjects_result:
            suggestions.append({
                "type": "subject",
                "id": subject_id,
                "text": subject_name,
                "category": "Subjects"
            })
        
        # Search topics
        topics_query = select(Topic.id, Topic.name).where(
            Topic.name.ilike(search_term)
        ).limit(limit // 3)
        
        topics_result = await db.execute(topics_query)
        for topic_id, topic_name in topics_result:
            suggestions.append({
                "type": "topic",
                "id": topic_id,
                "text": topic_name,
                "category": "Topics"
            })
        
        # Search question titles
        questions_query = select(Question.id, Question.title).where(
            Question.title.ilike(search_term)
        ).limit(limit // 3)
        
        questions_result = await db.execute(questions_query)
        for question_id, question_title in questions_result:
            suggestions.append({
                "type": "question",
                "id": question_id,
                "text": question_title[:100] + "..." if len(question_title) > 100 else question_title,
                "category": "Questions"
            })
        
        return suggestions[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending", response_model=Dict[str, Any])
async def get_trending_searches(
    period: str = Query("week", description="Period: 'day', 'week', 'month'"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get trending searches (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In a real app, you would track search queries and analyze trends
        
        trending_by_period = {
            "day": [
                "algebra", "calculus", "physics", "chemistry", "biology"
            ],
            "week": [
                "linear equations", "derivatives", "molecular structure", 
                "cell division", "geometry"
            ],
            "month": [
                "trigonometry", "organic chemistry", "genetics", 
                "probability", "statistics"
            ]
        }
        
        trending_terms = trending_by_period.get(period, trending_by_period["week"])
        
        return {
            "period": period,
            "trending_searches": trending_terms[:limit],
            "updated_at": "2024-01-01T00:00:00Z"  # Would be real timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_search_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's search history (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In a real app, you would store and retrieve actual search history
        
        # For now, return empty list
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history")
async def clear_search_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear user's search history"""
    try:
        # Placeholder implementation
        return {"message": "Search history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
