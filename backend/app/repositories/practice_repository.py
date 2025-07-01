from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case
from datetime import datetime, timedelta

from app.models.practice import (
    PracticeSession, UserAttempt, UserBookmark, UserProgress,
    SessionType, SessionStatus, AttemptStatus
)
from app.models.user import UserProfile, UserPreferences
from app.models.question import Question
from app.models.subject import Subject, Topic
from app.schemas.practice import (
    PracticeSessionCreate, PracticeSessionUpdate,
    UserAttemptCreate, UserAttemptUpdate,
    UserBookmarkCreate, UserBookmarkUpdate,
    UserProgressCreate, UserProgressUpdate,
    UserProfileCreate, UserProfileUpdate,
    UserPreferencesCreate, UserPreferencesUpdate
)
from app.repositories.base import BaseRepository

class PracticeSessionRepository(BaseRepository[PracticeSession, PracticeSessionCreate, PracticeSessionUpdate]):
    
    async def get_by_user(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[PracticeSession]:
        """Get practice sessions for a user"""
        return await self.get_multi_by_attribute(db, attribute="user_id", value=user_id, skip=skip, limit=limit)
    
    async def get_active_sessions(self, db: AsyncSession, *, user_id: int) -> List[PracticeSession]:
        """Get active (not completed) sessions for a user"""
        statement = (
            select(PracticeSession)
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.status.in_([SessionStatus.STARTED, SessionStatus.IN_PROGRESS, SessionStatus.PAUSED])
            ))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_subject(self, db: AsyncSession, *, user_id: int, subject_id: int, skip: int = 0, limit: int = 100) -> List[PracticeSession]:
        """Get sessions for a specific subject"""
        statement = (
            select(PracticeSession)
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.subject_id == subject_id
            ))
            .order_by(desc(PracticeSession.started_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_type(self, db: AsyncSession, *, user_id: int, session_type: SessionType, skip: int = 0, limit: int = 100) -> List[PracticeSession]:
        """Get sessions by type"""
        statement = (
            select(PracticeSession)
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.session_type == session_type
            ))
            .order_by(desc(PracticeSession.started_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_with_attempts(self, db: AsyncSession, *, session_id: int) -> Optional[PracticeSession]:
        """Get session with all attempts loaded"""
        statement = (
            select(PracticeSession)
            .options(selectinload(PracticeSession.attempts))
            .where(PracticeSession.id == session_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_completed_sessions(self, db: AsyncSession, *, user_id: int, days: int = 30) -> List[PracticeSession]:
        """Get completed sessions within the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        statement = (
            select(PracticeSession)
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.status == SessionStatus.COMPLETED,
                PracticeSession.completed_at >= since_date
            ))
            .order_by(desc(PracticeSession.completed_at))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def update_session_progress(self, db: AsyncSession, *, session_id: int, 
                                    correct_answers: int, incorrect_answers: int, 
                                    skipped_questions: int, time_spent: int) -> Optional[PracticeSession]:
        """Update session progress metrics"""
        session = await self.get(db, id=session_id)
        if session:
            session.correct_answers = correct_answers
            session.incorrect_answers = incorrect_answers
            session.skipped_questions = skipped_questions
            session.total_time_spent = time_spent
            session.total_questions = correct_answers + incorrect_answers + skipped_questions
            
            if session.total_questions > 0:
                session.score_percentage = (correct_answers / session.total_questions) * 100
            
            if session.total_questions > 0 and time_spent > 0:
                session.average_time_per_question = time_spent / session.total_questions
            
            db.add(session)
            await db.flush()
            await db.refresh(session)
        
        return session
    
    async def complete_session(self, db: AsyncSession, *, session_id: int) -> Optional[PracticeSession]:
        """Mark session as completed"""
        session = await self.get(db, id=session_id)
        if session:
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.utcnow()
            
            db.add(session)
            await db.flush()
            await db.refresh(session)
        
        return session
    
    async def get_user_statistics(self, db: AsyncSession, *, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user's practice session statistics"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Total sessions
        total_sessions = await db.execute(
            select(func.count(PracticeSession.id))
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.started_at >= since_date
            ))
        )
        
        # Completed sessions
        completed_sessions = await db.execute(
            select(func.count(PracticeSession.id))
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.status == SessionStatus.COMPLETED,
                PracticeSession.started_at >= since_date
            ))
        )
        
        # Average score
        avg_score = await db.execute(
            select(func.avg(PracticeSession.score_percentage))
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.status == SessionStatus.COMPLETED,
                PracticeSession.started_at >= since_date
            ))
        )
        
        # Total study time
        total_time = await db.execute(
            select(func.sum(PracticeSession.total_time_spent))
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.status == SessionStatus.COMPLETED,
                PracticeSession.started_at >= since_date
            ))
        )
        
        # Sessions by type
        sessions_by_type = await db.execute(
            select(PracticeSession.session_type, func.count(PracticeSession.id))
            .where(and_(
                PracticeSession.user_id == user_id,
                PracticeSession.started_at >= since_date
            ))
            .group_by(PracticeSession.session_type)
        )
        
        return {
            "total_sessions": total_sessions.scalar() or 0,
            "completed_sessions": completed_sessions.scalar() or 0,
            "average_score": float(avg_score.scalar() or 0),
            "total_study_time": int(total_time.scalar() or 0),
            "sessions_by_type": dict(sessions_by_type.all()),
            "completion_rate": ((completed_sessions.scalar() or 0) / max(total_sessions.scalar() or 1, 1)) * 100
        }

class UserAttemptRepository(BaseRepository[UserAttempt, UserAttemptCreate, UserAttemptUpdate]):
    
    async def get_by_user(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[UserAttempt]:
        return await self.get_multi_by_attribute(db, attribute="user_id", value=user_id, skip=skip, limit=limit)
    
    async def get_by_question(self, db: AsyncSession, *, question_id: int, skip: int = 0, limit: int = 100) -> List[UserAttempt]:
        return await self.get_multi_by_attribute(db, attribute="question_id", value=question_id, skip=skip, limit=limit)
    
    async def get_by_session(self, db: AsyncSession, *, session_id: int) -> List[UserAttempt]:
        return await self.get_multi_by_attribute(db, attribute="session_id", value=session_id)
    
    async def get_user_question_attempts(self, db: AsyncSession, *, user_id: int, question_id: int) -> List[UserAttempt]:
        """Get all attempts by a user for a specific question"""
        statement = (
            select(UserAttempt)
            .where(and_(
                UserAttempt.user_id == user_id,
                UserAttempt.question_id == question_id
            ))
            .order_by(asc(UserAttempt.created_at))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_correct_attempts(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[UserAttempt]:
        statement = (
            select(UserAttempt)
            .where(and_(
                UserAttempt.user_id == user_id,
                UserAttempt.is_correct == True
            ))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_incorrect_attempts(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[UserAttempt]:
        statement = (
            select(UserAttempt)
            .where(and_(
                UserAttempt.user_id == user_id,
                UserAttempt.is_correct == False
            ))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_recent_attempts(self, db: AsyncSession, *, user_id: int, days: int = 7) -> List[UserAttempt]:
        """Get recent attempts within the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        statement = (
            select(UserAttempt)
            .where(and_(
                UserAttempt.user_id == user_id,
                UserAttempt.created_at >= since_date
            ))
            .order_by(desc(UserAttempt.created_at))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_performance_by_subject(self, db: AsyncSession, *, user_id: int, subject_id: int) -> Dict[str, Any]:
        """Get user performance statistics for a specific subject"""
        statement = (
            select(
                func.count(UserAttempt.id).label('total'),
                func.sum(case((UserAttempt.is_correct == True, 1), else_=0)).label('correct'),
                func.avg(UserAttempt.time_taken).label('avg_time'),
                func.avg(UserAttempt.confidence_level).label('avg_confidence')
            )
            .join(Question)
            .where(and_(
                UserAttempt.user_id == user_id,
                Question.subject_id == subject_id
            ))
        )
        result = await db.execute(statement)
        stats = result.first()
        
        total = stats.total or 0
        correct = stats.correct or 0
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy_percentage": accuracy,
            "average_time": float(stats.avg_time or 0),
            "average_confidence": float(stats.avg_confidence or 0)
        }
    
    async def get_learning_analytics(self, db: AsyncSession, *, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get detailed learning analytics for a user"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Performance over time
        daily_performance = await db.execute(
            select(
                func.date(UserAttempt.created_at).label('date'),
                func.count(UserAttempt.id).label('attempts'),
                func.avg(case((UserAttempt.is_correct == True, 1.0), else_=0.0)).label('accuracy')
            )
            .where(and_(
                UserAttempt.user_id == user_id,
                UserAttempt.created_at >= since_date
            ))
            .group_by(func.date(UserAttempt.created_at))
            .order_by(func.date(UserAttempt.created_at))
        )
        
        # Difficulty analysis
        difficulty_performance = await db.execute(
            select(
                Question.difficulty_level,
                func.count(UserAttempt.id).label('attempts'),
                func.avg(case((UserAttempt.is_correct == True, 1.0), else_=0.0)).label('accuracy')
            )
            .join(Question)
            .where(and_(
                UserAttempt.user_id == user_id,
                UserAttempt.created_at >= since_date
            ))
            .group_by(Question.difficulty_level)
        )
        
        return {
            "daily_performance": [
                {
                    "date": str(row.date),
                    "attempts": row.attempts,
                    "accuracy": float(row.accuracy or 0) * 100
                }
                for row in daily_performance.all()
            ],
            "difficulty_performance": {
                row.difficulty_level.value: {
                    "attempts": row.attempts,
                    "accuracy": float(row.accuracy or 0) * 100
                }
                for row in difficulty_performance.all()
            }
        }

class UserBookmarkRepository(BaseRepository[UserBookmark, UserBookmarkCreate, UserBookmarkUpdate]):
    
    async def get_by_user(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[UserBookmark]:
        return await self.get_multi_by_attribute(db, attribute="user_id", value=user_id, skip=skip, limit=limit)
    
    async def get_active_bookmarks(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[UserBookmark]:
        statement = (
            select(UserBookmark)
            .where(and_(
                UserBookmark.user_id == user_id,
                UserBookmark.is_active == True
            ))
            .order_by(desc(UserBookmark.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_type(self, db: AsyncSession, *, user_id: int, bookmark_type: str, skip: int = 0, limit: int = 100) -> List[UserBookmark]:
        statement = (
            select(UserBookmark)
            .where(and_(
                UserBookmark.user_id == user_id,
                UserBookmark.bookmark_type == bookmark_type,
                UserBookmark.is_active == True
            ))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_priority(self, db: AsyncSession, *, user_id: int, min_priority: int = 3) -> List[UserBookmark]:
        statement = (
            select(UserBookmark)
            .where(and_(
                UserBookmark.user_id == user_id,
                UserBookmark.priority >= min_priority,
                UserBookmark.is_active == True
            ))
            .order_by(desc(UserBookmark.priority))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_due_for_review(self, db: AsyncSession, *, user_id: int) -> List[UserBookmark]:
        """Get bookmarks that are due for review"""
        statement = (
            select(UserBookmark)
            .where(and_(
                UserBookmark.user_id == user_id,
                UserBookmark.target_review_date <= datetime.utcnow(),
                UserBookmark.is_active == True,
                UserBookmark.is_mastered == False
            ))
            .order_by(asc(UserBookmark.target_review_date))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def check_bookmark_exists(self, db: AsyncSession, *, user_id: int, question_id: int) -> Optional[UserBookmark]:
        """Check if a bookmark already exists"""
        statement = (
            select(UserBookmark)
            .where(and_(
                UserBookmark.user_id == user_id,
                UserBookmark.question_id == question_id
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def mark_as_reviewed(self, db: AsyncSession, *, bookmark_id: int) -> Optional[UserBookmark]:
        """Mark bookmark as reviewed"""
        bookmark = await self.get(db, id=bookmark_id)
        if bookmark:
            bookmark.review_count += 1
            bookmark.last_reviewed_at = datetime.utcnow()
            
            # Set next review date (spaced repetition logic)
            days_to_add = min(bookmark.review_count * 2, 30)  # Exponential backoff, max 30 days
            bookmark.target_review_date = datetime.utcnow() + timedelta(days=days_to_add)
            
            db.add(bookmark)
            await db.flush()
            await db.refresh(bookmark)
        
        return bookmark

class UserProgressRepository(BaseRepository[UserProgress, UserProgressCreate, UserProgressUpdate]):
    
    async def get_by_user(self, db: AsyncSession, *, user_id: int) -> List[UserProgress]:
        return await self.get_multi_by_attribute(db, attribute="user_id", value=user_id)
    
    async def get_by_subject(self, db: AsyncSession, *, user_id: int, subject_id: int) -> Optional[UserProgress]:
        statement = (
            select(UserProgress)
            .where(and_(
                UserProgress.user_id == user_id,
                UserProgress.subject_id == subject_id,
                UserProgress.topic_id.is_(None)  # Subject-level progress
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_topic(self, db: AsyncSession, *, user_id: int, topic_id: int) -> Optional[UserProgress]:
        statement = (
            select(UserProgress)
            .where(and_(
                UserProgress.user_id == user_id,
                UserProgress.topic_id == topic_id
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_subject_progress_overview(self, db: AsyncSession, *, user_id: int) -> List[UserProgress]:
        """Get progress overview for all subjects"""
        statement = (
            select(UserProgress)
            .where(and_(
                UserProgress.user_id == user_id,
                UserProgress.topic_id.is_(None)  # Only subject-level progress
            ))
            .order_by(desc(UserProgress.mastery_level))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def update_progress_from_attempt(self, db: AsyncSession, *, user_id: int, subject_id: int, 
                                         topic_id: Optional[int], is_correct: bool, time_taken: float) -> UserProgress:
        """Update progress based on a new attempt"""
        # Get or create subject progress
        progress = await self.get_by_subject(db, user_id=user_id, subject_id=subject_id)
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                subject_id=subject_id,
                topic_id=None
            )
            db.add(progress)
            await db.flush()
        
        # Update metrics
        progress.total_questions_attempted += 1
        if is_correct:
            progress.correct_answers += 1
        else:
            progress.incorrect_answers += 1
        
        # Recalculate accuracy
        if progress.total_questions_attempted > 0:
            progress.accuracy_rate = (progress.correct_answers / progress.total_questions_attempted) * 100
        
        # Update average time
        if progress.average_time_per_question:
            progress.average_time_per_question = (
                (progress.average_time_per_question * (progress.total_questions_attempted - 1) + time_taken) 
                / progress.total_questions_attempted
            )
        else:
            progress.average_time_per_question = time_taken
        
        # Update mastery level (simple algorithm, can be enhanced)
        if progress.total_questions_attempted >= 10:
            progress.mastery_level = min(progress.accuracy_rate / 100, 1.0)
        
        progress.last_practiced_at = datetime.utcnow()
        
        db.add(progress)
        await db.flush()
        await db.refresh(progress)
        
        # Handle topic progress if applicable
        if topic_id:
            topic_progress = await self.get_by_topic(db, user_id=user_id, topic_id=topic_id)
            if not topic_progress:
                topic_progress = UserProgress(
                    user_id=user_id,
                    subject_id=subject_id,
                    topic_id=topic_id
                )
                db.add(topic_progress)
                await db.flush()
            
            # Update topic progress similarly
            topic_progress.total_questions_attempted += 1
            if is_correct:
                topic_progress.correct_answers += 1
            else:
                topic_progress.incorrect_answers += 1
            
            if topic_progress.total_questions_attempted > 0:
                topic_progress.accuracy_rate = (topic_progress.correct_answers / topic_progress.total_questions_attempted) * 100
            
            topic_progress.last_practiced_at = datetime.utcnow()
            
            db.add(topic_progress)
            await db.flush()
            await db.refresh(topic_progress)
        
        return progress

class UserProfileRepository(BaseRepository[UserProfile, UserProfileCreate, UserProfileUpdate]):
    
    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Optional[UserProfile]:
        return await self.get_by_attribute(db, attribute="user_id", value=user_id)
    
    async def get_by_university(self, db: AsyncSession, *, university: str, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        return await self.get_multi_by_attribute(db, attribute="university", value=university, skip=skip, limit=limit)

class UserPreferencesRepository(BaseRepository[UserPreferences, UserPreferencesCreate, UserPreferencesUpdate]):
    
    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Optional[UserPreferences]:
        return await self.get_by_attribute(db, attribute="user_id", value=user_id)

# Initialize repository instances
practice_session_repo = PracticeSessionRepository(PracticeSession)
user_attempt_repo = UserAttemptRepository(UserAttempt)
user_bookmark_repo = UserBookmarkRepository(UserBookmark)
user_progress_repo = UserProgressRepository(UserProgress)
user_profile_repo = UserProfileRepository(UserProfile)
user_preferences_repo = UserPreferencesRepository(UserPreferences)
