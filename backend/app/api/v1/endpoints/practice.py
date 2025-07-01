from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.practice import (
    PracticeSessionCreate, PracticeSessionRead, PracticeSessionUpdate,
    UserAttemptCreate, UserAttemptRead, UserAttemptUpdate,
    UserBookmarkCreate, UserBookmarkRead, UserProgressRead,
    UserProfileRead, UserProfileUpdate, UserPreferencesRead, UserPreferencesUpdate
)
from app.api.deps import get_current_active_user
from app.services.practice_service import PracticeService

router = APIRouter()

# Practice Session endpoints
@router.post("/sessions", response_model=PracticeSessionRead)
async def create_practice_session(
    session_data: PracticeSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new practice session"""
    try:
        service = PracticeService(db)
        session = await service.create_session(current_user.id, session_data)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[PracticeSessionRead])
async def get_user_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by session status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's practice sessions"""
    try:
        service = PracticeService(db)
        sessions = await service.get_user_sessions(
            current_user.id, skip, limit, status
        )
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=PracticeSessionRead)
async def get_practice_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific practice session"""
    try:
        service = PracticeService(db)
        session = await service.get(session_id)
        
        if not session or session.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}/complete", response_model=PracticeSessionRead)
async def complete_practice_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete a practice session"""
    try:
        service = PracticeService(db)
        session = await service.complete_session(session_id, current_user.id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Attempt endpoints
@router.post("/attempts", response_model=UserAttemptRead)
async def submit_attempt(
    attempt_data: UserAttemptCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a user attempt for a question"""
    try:
        service = PracticeService(db)
        
        # Set user_id from current user
        attempt_dict = attempt_data.dict()
        attempt_dict["user_id"] = current_user.id
        
        # Create the attempt object
        from app.schemas.practice import UserAttemptCreate
        attempt_with_user = UserAttemptCreate(**attempt_dict)
        
        attempt = await service.submit_attempt(attempt_with_user)
        return attempt
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attempts", response_model=List[UserAttemptRead])
async def get_user_attempts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    question_id: Optional[int] = Query(None, description="Filter by question ID"),
    session_id: Optional[int] = Query(None, description="Filter by session ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's attempts"""
    try:
        service = PracticeService(db)
        attempts = await service.get_user_attempts(
            current_user.id, question_id, session_id, skip, limit
        )
        return attempts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attempts/{attempt_id}", response_model=UserAttemptRead)
async def get_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific attempt"""
    try:
        from app.models.practice import UserAttempt
        from sqlalchemy import select
        
        query = select(UserAttempt).where(
            UserAttempt.id == attempt_id,
            UserAttempt.user_id == current_user.id
        )
        result = await db.execute(query)
        attempt = result.scalar_one_or_none()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        
        return attempt
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Bookmark endpoints
@router.post("/bookmarks", response_model=UserBookmarkRead)
async def add_bookmark(
    bookmark_data: UserBookmarkCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a bookmark"""
    try:
        service = PracticeService(db)
        bookmark = await service.add_bookmark(current_user.id, bookmark_data)
        return bookmark
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookmarks", response_model=List[UserBookmarkRead])
async def get_user_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    bookmark_type: Optional[str] = Query(None, description="Filter by bookmark type"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bookmarks"""
    try:
        service = PracticeService(db)
        bookmarks = await service.get_user_bookmarks(
            current_user.id, bookmark_type, skip, limit
        )
        return bookmarks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/bookmarks/{bookmark_id}")
async def remove_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a bookmark"""
    try:
        from app.models.practice import UserBookmark
        from sqlalchemy import select
        
        query = select(UserBookmark).where(
            UserBookmark.id == bookmark_id,
            UserBookmark.user_id == current_user.id
        )
        result = await db.execute(query)
        bookmark = result.scalar_one_or_none()
        
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")
        
        await db.delete(bookmark)
        await db.commit()
        
        return {"message": "Bookmark removed successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Progress endpoints
@router.get("/progress", response_model=List[UserProgressRead])
async def get_user_progress(
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's progress"""
    try:
        service = PracticeService(db)
        progress = await service.get_user_progress(current_user.id, subject_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress/summary", response_model=Dict[str, Any])
async def get_progress_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's progress summary"""
    try:
        service = PracticeService(db)
        progress_list = await service.get_user_progress(current_user.id)
        
        # Calculate summary statistics
        total_questions = sum(p.total_questions_attempted for p in progress_list)
        total_correct = sum(p.correct_answers for p in progress_list)
        total_sessions = sum(p.sessions_completed for p in progress_list)
        total_study_time = sum(p.total_study_time for p in progress_list)
        
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Subject breakdown
        subject_breakdown = {}
        for progress in progress_list:
            if progress.subject and progress.subject.name:
                subject_name = progress.subject.name
                if subject_name not in subject_breakdown:
                    subject_breakdown[subject_name] = {
                        "questions_attempted": 0,
                        "correct_answers": 0,
                        "accuracy_rate": 0
                    }
                
                subject_breakdown[subject_name]["questions_attempted"] += progress.total_questions_attempted
                subject_breakdown[subject_name]["correct_answers"] += progress.correct_answers
                
                # Recalculate accuracy for this subject
                attempted = subject_breakdown[subject_name]["questions_attempted"]
                correct = subject_breakdown[subject_name]["correct_answers"]
                subject_breakdown[subject_name]["accuracy_rate"] = (correct / attempted * 100) if attempted > 0 else 0
        
        return {
            "total_questions_attempted": total_questions,
            "total_correct_answers": total_correct,
            "overall_accuracy_rate": overall_accuracy,
            "total_practice_sessions": total_sessions,
            "total_study_time_minutes": total_study_time,
            "subject_breakdown": subject_breakdown,
            "subjects_studied": len(subject_breakdown)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Profile endpoints
@router.get("/profile", response_model=UserProfileRead)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's profile"""
    try:
        service = PracticeService(db)
        profile = await service.get_user_profile(current_user.id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=UserProfileRead)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's profile"""
    try:
        service = PracticeService(db)
        profile = await service.update_user_profile(current_user.id, profile_data)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Preferences endpoints
@router.get("/preferences", response_model=UserPreferencesRead)
async def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's preferences"""
    try:
        service = PracticeService(db)
        preferences = await service.get_user_preferences(current_user.id)
        
        if not preferences:
            raise HTTPException(status_code=404, detail="Preferences not found")
        
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/preferences", response_model=UserPreferencesRead)
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's preferences"""
    try:
        service = PracticeService(db)
        preferences = await service.update_user_preferences(current_user.id, preferences_data)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_practice_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's practice statistics"""
    try:
        from app.models.practice import PracticeSession, UserAttempt
        from sqlalchemy import select, func
        
        # Get session stats
        session_stats_query = select(
            func.count(PracticeSession.id).label('total_sessions'),
            func.avg(PracticeSession.score_percentage).label('avg_score'),
            func.sum(PracticeSession.total_time_spent).label('total_time')
        ).where(PracticeSession.user_id == current_user.id)
        
        session_result = await db.execute(session_stats_query)
        session_stats = session_result.first()
        
        # Get attempt stats
        attempt_stats_query = select(
            func.count(UserAttempt.id).label('total_attempts'),
            func.sum(func.case((UserAttempt.is_correct == True, 1), else_=0)).label('correct_attempts')
        ).where(UserAttempt.user_id == current_user.id)
        
        attempt_result = await db.execute(attempt_stats_query)
        attempt_stats = attempt_result.first()
        
        total_attempts = attempt_stats.total_attempts or 0
        correct_attempts = attempt_stats.correct_attempts or 0
        accuracy_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "total_practice_sessions": session_stats.total_sessions or 0,
            "average_session_score": session_stats.avg_score or 0,
            "total_study_time_minutes": session_stats.total_time or 0,
            "total_question_attempts": total_attempts,
            "correct_answers": correct_attempts,
            "overall_accuracy_rate": accuracy_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
