from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case
from datetime import datetime, timedelta

from app.models.user import User, UserProfile, UserPreferences
from app.models.practice import UserProgress, UserAttempt, UserBookmark
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        return await self.get_by_attribute(db, attribute="email", value=email)
    
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        return await self.get_by_attribute(db, attribute="username", value=username)
    
    async def is_active(self, user: User) -> bool:
        return user.is_active
    
    async def is_superuser(self, user: User) -> bool:
        return user.is_superuser
    
    async def create_user(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        return await self.create(db, obj_in=obj_in)
    
    async def get_with_profile(self, db: AsyncSession, *, user_id: int) -> Optional[User]:
        """Get user with profile and preferences loaded"""
        statement = (
            select(User)
            .options(
                selectinload(User.profile),
                selectinload(User.preferences)
            )
            .where(User.id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_active_users(self, db: AsyncSession, *, days: int = 7, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users who have been active in the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        statement = (
            select(User)
            .join(UserAttempt)
            .where(UserAttempt.created_at >= since_date)
            .distinct()
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_users_by_university(self, db: AsyncSession, *, university: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users from a specific university"""
        statement = (
            select(User)
            .join(UserProfile)
            .where(UserProfile.university == university)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def search_users(self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by username or email"""
        search_filter = or_(
            User.username.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%")
        )
        
        statement = (
            select(User)
            .where(and_(User.is_active == True, search_filter))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_user_statistics(self, db: AsyncSession, *, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        # Total attempts
        total_attempts = await db.execute(
            select(func.count(UserAttempt.id))
            .where(UserAttempt.user_id == user_id)
        )
        
        # Correct attempts
        correct_attempts = await db.execute(
            select(func.count(UserAttempt.id))
            .where(and_(
                UserAttempt.user_id == user_id,
                UserAttempt.is_correct == True
            ))
        )
        
        # Total bookmarks
        total_bookmarks = await db.execute(
            select(func.count(UserBookmark.id))
            .where(and_(
                UserBookmark.user_id == user_id,
                UserBookmark.is_active == True
            ))
        )
        
        # Subjects studied
        subjects_studied = await db.execute(
            select(func.count(func.distinct(UserProgress.subject_id)))
            .where(UserProgress.user_id == user_id)
        )
        
        # Average time per question
        avg_time = await db.execute(
            select(func.avg(UserAttempt.time_taken))
            .where(UserAttempt.user_id == user_id)
        )
        
        # Study streak (consecutive days with activity)
        study_streak = await self._calculate_study_streak(db, user_id=user_id)
        
        total = total_attempts.scalar() or 0
        correct = correct_attempts.scalar() or 0
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy_percentage": accuracy,
            "total_bookmarks": total_bookmarks.scalar() or 0,
            "subjects_studied": subjects_studied.scalar() or 0,
            "average_time_per_question": float(avg_time.scalar() or 0),
            "current_study_streak": study_streak
        }
    
    async def _calculate_study_streak(self, db: AsyncSession, *, user_id: int) -> int:
        """Calculate the current study streak for a user"""
        # Get daily activity for the last 30 days
        statement = (
            select(func.date(UserAttempt.created_at).label('date'))
            .where(UserAttempt.user_id == user_id)
            .where(UserAttempt.created_at >= datetime.utcnow() - timedelta(days=30))
            .group_by(func.date(UserAttempt.created_at))
            .order_by(desc(func.date(UserAttempt.created_at)))
        )
        result = await db.execute(statement)
        activity_dates = [row.date for row in result.all()]
        
        if not activity_dates:
            return 0
        
        # Calculate streak
        streak = 0
        today = datetime.utcnow().date()
        current_date = today
        
        for activity_date in activity_dates:
            if activity_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif activity_date == current_date + timedelta(days=1):
                # Allow for yesterday if today hasn't been active yet
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    async def get_leaderboard(self, db: AsyncSession, *, metric: str = "accuracy", days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user leaderboard based on different metrics"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        if metric == "accuracy":
            statement = (
                select(
                    User.username,
                    func.count(UserAttempt.id).label('total_attempts'),
                    func.sum(case((UserAttempt.is_correct == True, 1), else_=0)).label('correct_attempts'),
                    (func.sum(case((UserAttempt.is_correct == True, 1), else_=0)) * 100.0 / func.count(UserAttempt.id)).label('accuracy')
                )
                .join(UserAttempt)
                .where(and_(
                    UserAttempt.created_at >= since_date,
                    User.is_active == True
                ))
                .group_by(User.id, User.username)
                .having(func.count(UserAttempt.id) >= 10)  # Minimum attempts for ranking
                .order_by(desc('accuracy'))
                .limit(limit)
            )
        elif metric == "volume":
            statement = (
                select(
                    User.username,
                    func.count(UserAttempt.id).label('total_attempts')
                )
                .join(UserAttempt)
                .where(and_(
                    UserAttempt.created_at >= since_date,
                    User.is_active == True
                ))
                .group_by(User.id, User.username)
                .order_by(desc('total_attempts'))
                .limit(limit)
            )
        else:
            raise ValueError(f"Unsupported metric: {metric}")
        
        result = await db.execute(statement)
        
        if metric == "accuracy":
            return [
                {
                    "username": row.username,
                    "total_attempts": row.total_attempts,
                    "correct_attempts": row.correct_attempts,
                    "accuracy": float(row.accuracy)
                }
                for row in result.all()
            ]
        else:
            return [
                {
                    "username": row.username,
                    "total_attempts": row.total_attempts
                }
                for row in result.all()
            ]
    
    async def update_last_login(self, db: AsyncSession, *, user_id: int) -> Optional[User]:
        """Update user's last login timestamp"""
        user = await self.get(db, id=user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            db.add(user)
            await db.flush()
            await db.refresh(user)
        return user
    
    async def deactivate_user(self, db: AsyncSession, *, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        user = await self.get(db, id=user_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.add(user)
            await db.flush()
            await db.refresh(user)
        return user
    
    async def reactivate_user(self, db: AsyncSession, *, user_id: int) -> Optional[User]:
        """Reactivate a user account"""
        user = await self.get(db, id=user_id)
        if user:
            user.is_active = True
            user.updated_at = datetime.utcnow()
            db.add(user)
            await db.flush()
            await db.refresh(user)
        return user

# Initialize repository instance for use in services/endpoints
user_repo = UserRepository(User)
