from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from datetime import datetime, timedelta
import logging

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
    UserBookmarkCreate, UserProgressUpdate,
    UserProfileCreate, UserProfileUpdate,
    UserPreferencesCreate, UserPreferencesUpdate
)
from app.services.base import BaseService

logger = logging.getLogger(__name__)

class PracticeService(BaseService[PracticeSession, PracticeSessionCreate, PracticeSessionUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(PracticeSession, db)
    
    async def create_session(self, user_id: int, session_data: PracticeSessionCreate) -> PracticeSession:
        """Create a new practice session"""
        try:
            session_dict = session_data.dict()
            session_dict["user_id"] = user_id
            session_dict["status"] = SessionStatus.STARTED
            session_dict["started_at"] = datetime.utcnow()
            
            session = PracticeSession(**session_dict)
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            return session
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating practice session: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_sessions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[SessionStatus] = None
    ) -> List[PracticeSession]:
        """Get practice sessions for a user"""
        try:
            query = select(PracticeSession).options(
                selectinload(PracticeSession.subject),
                selectinload(PracticeSession.topic)
            ).where(PracticeSession.user_id == user_id)
            
            if status:
                query = query.where(PracticeSession.status == status)
            
            query = query.order_by(desc(PracticeSession.created_at))
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user sessions for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def complete_session(self, session_id: int, user_id: int) -> PracticeSession:
        """Complete a practice session and calculate results"""
        try:
            # Get session with attempts
            query = select(PracticeSession).options(
                selectinload(PracticeSession.attempts)
            ).where(
                and_(
                    PracticeSession.id == session_id,
                    PracticeSession.user_id == user_id
                )
            )
            
            result = await self.db.execute(query)
            session = result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Calculate session results
            total_questions = len(session.attempts)
            correct_answers = sum(1 for attempt in session.attempts if attempt.is_correct)
            incorrect_answers = sum(1 for attempt in session.attempts if not attempt.is_correct and attempt.status != AttemptStatus.SKIPPED)
            skipped_questions = sum(1 for attempt in session.attempts if attempt.status == AttemptStatus.SKIPPED)
            
            score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Calculate timing stats
            completed_attempts = [a for a in session.attempts if a.time_taken is not None]
            if completed_attempts:
                times = [a.time_taken for a in completed_attempts]
                avg_time = sum(times) / len(times)
                fastest_time = min(times)
                slowest_time = max(times)
            else:
                avg_time = fastest_time = slowest_time = None
            
            # Update session
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.utcnow()
            session.total_questions = total_questions
            session.correct_answers = correct_answers
            session.incorrect_answers = incorrect_answers
            session.skipped_questions = skipped_questions
            session.score_percentage = score_percentage
            session.average_time_per_question = avg_time
            session.fastest_answer_time = fastest_time
            session.slowest_answer_time = slowest_time
            
            await self.db.commit()
            await self.db.refresh(session)
            
            # Update user progress
            await self._update_user_progress(user_id, session)
            
            return session
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error completing session {session_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def submit_attempt(self, attempt_data: UserAttemptCreate) -> UserAttempt:
        """Submit a user attempt for a question"""
        try:
            attempt_dict = attempt_data.dict()
            attempt_dict["submitted_at"] = datetime.utcnow()
            
            # Get the question to check correct answer
            question_query = select(Question).where(Question.id == attempt_data.question_id)
            question_result = await self.db.execute(question_query)
            question = question_result.scalar_one_or_none()
            
            if question:
                # Simple answer checking (would be more sophisticated in real implementation)
                if attempt_data.user_answer and question.answer:
                    attempt_dict["is_correct"] = attempt_data.user_answer.strip().lower() == question.answer.strip().lower()
                    attempt_dict["status"] = AttemptStatus.CORRECT if attempt_dict["is_correct"] else AttemptStatus.INCORRECT
            
            attempt = UserAttempt(**attempt_dict)
            self.db.add(attempt)
            await self.db.commit()
            await self.db.refresh(attempt)
            return attempt
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error submitting attempt: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_attempts(
        self,
        user_id: int,
        question_id: Optional[int] = None,
        session_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[UserAttempt]:
        """Get user attempts with optional filtering"""
        try:
            query = select(UserAttempt).options(
                selectinload(UserAttempt.question)
            ).where(UserAttempt.user_id == user_id)
            
            if question_id:
                query = query.where(UserAttempt.question_id == question_id)
            
            if session_id:
                query = query.where(UserAttempt.session_id == session_id)
            
            query = query.order_by(desc(UserAttempt.created_at))
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user attempts: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def add_bookmark(self, user_id: int, bookmark_data: UserBookmarkCreate) -> UserBookmark:
        """Add a bookmark for a user"""
        try:
            # Check if bookmark already exists
            existing_query = select(UserBookmark).where(
                and_(
                    UserBookmark.user_id == user_id,
                    UserBookmark.question_id == bookmark_data.question_id
                )
            )
            existing_result = await self.db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                raise HTTPException(status_code=400, detail="Question already bookmarked")
            
            bookmark_dict = bookmark_data.dict()
            bookmark_dict["user_id"] = user_id
            
            bookmark = UserBookmark(**bookmark_dict)
            self.db.add(bookmark)
            await self.db.commit()
            await self.db.refresh(bookmark)
            return bookmark
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding bookmark: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_bookmarks(
        self,
        user_id: int,
        bookmark_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[UserBookmark]:
        """Get user bookmarks"""
        try:
            query = select(UserBookmark).options(
                selectinload(UserBookmark.question)
            ).where(UserBookmark.user_id == user_id)
            
            if bookmark_type:
                query = query.where(UserBookmark.bookmark_type == bookmark_type)
            
            query = query.order_by(desc(UserBookmark.created_at))
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user bookmarks: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_progress(self, user_id: int, subject_id: Optional[int] = None) -> List[UserProgress]:
        """Get user progress"""
        try:
            query = select(UserProgress).options(
                selectinload(UserProgress.subject),
                selectinload(UserProgress.topic)
            ).where(UserProgress.user_id == user_id)
            
            if subject_id:
                query = query.where(UserProgress.subject_id == subject_id)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user progress: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def _update_user_progress(self, user_id: int, session: PracticeSession):
        """Update user progress based on session results"""
        try:
            if not session.subject_id:
                return
            
            # Get or create progress record
            progress_query = select(UserProgress).where(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.subject_id == session.subject_id,
                    UserProgress.topic_id == session.topic_id
                )
            )
            progress_result = await self.db.execute(progress_query)
            progress = progress_result.scalar_one_or_none()
            
            if not progress:
                progress = UserProgress(
                    user_id=user_id,
                    subject_id=session.subject_id,
                    topic_id=session.topic_id
                )
                self.db.add(progress)
            
            # Update progress metrics
            progress.total_questions_attempted += session.total_questions
            progress.correct_answers += session.correct_answers
            progress.incorrect_answers += session.incorrect_answers
            progress.skipped_questions += session.skipped_questions
            progress.sessions_completed += 1
            progress.last_practiced_at = datetime.utcnow()
            
            # Recalculate accuracy rate
            total_answered = progress.correct_answers + progress.incorrect_answers
            if total_answered > 0:
                progress.accuracy_rate = (progress.correct_answers / total_answered) * 100
            
            # Update study time
            if session.total_time_spent:
                progress.total_study_time += session.total_time_spent
            
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error updating user progress: {str(e)}")
            # Don't raise exception here as this is a background operation
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile"""
        try:
            query = select(UserProfile).where(UserProfile.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> UserProfile:
        """Update or create user profile"""
        try:
            # Try to get existing profile
            profile = await self.get_user_profile(user_id)
            
            if profile:
                # Update existing profile
                for field, value in profile_data.dict(exclude_unset=True).items():
                    setattr(profile, field, value)
            else:
                # Create new profile
                profile_dict = profile_data.dict(exclude_unset=True)
                profile_dict["user_id"] = user_id
                profile = UserProfile(**profile_dict)
                self.db.add(profile)
            
            await self.db.commit()
            await self.db.refresh(profile)
            return profile
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        try:
            query = select(UserPreferences).where(UserPreferences.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update_user_preferences(self, user_id: int, preferences_data: UserPreferencesUpdate) -> UserPreferences:
        """Update or create user preferences"""
        try:
            # Try to get existing preferences
            preferences = await self.get_user_preferences(user_id)
            
            if preferences:
                # Update existing preferences
                for field, value in preferences_data.dict(exclude_unset=True).items():
                    setattr(preferences, field, value)
            else:
                # Create new preferences
                prefs_dict = preferences_data.dict(exclude_unset=True)
                prefs_dict["user_id"] = user_id
                preferences = UserPreferences(**prefs_dict)
                self.db.add(preferences)
            
            await self.db.commit()
            await self.db.refresh(preferences)
            return preferences
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user preferences: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
