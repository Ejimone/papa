from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case, cast, extract
from datetime import datetime, timedelta
import json

from app.models.analytics import (
    DailyUserActivity, WeeklyUserActivity, MonthlyUserActivity,
    SubjectPerformanceAnalytics, TopicPerformanceAnalytics,
    DifficultyLevelAnalytics, LearningPathAnalytics
)
from app.models.practice import UserAttempt, PracticeSession
from app.models.question import Question
from app.models.subject import Subject, Topic
from app.models.user import User
from app.schemas.analytics import (
    DailyUserActivityCreate, DailyUserActivityUpdate,
    WeeklyUserActivityCreate, WeeklyUserActivityUpdate,
    MonthlyUserActivityCreate, MonthlyUserActivityUpdate,
    SubjectPerformanceAnalyticsCreate, SubjectPerformanceAnalyticsUpdate,
    TopicPerformanceAnalyticsCreate, TopicPerformanceAnalyticsUpdate,
    DifficultyLevelAnalyticsCreate, DifficultyLevelAnalyticsUpdate,
    LearningPathAnalyticsCreate, LearningPathAnalyticsUpdate
)
from app.repositories.base import BaseRepository

class DailyUserActivityRepository(BaseRepository[DailyUserActivity, DailyUserActivityCreate, DailyUserActivityUpdate]):
    
    async def get_by_user_and_date(self, db: AsyncSession, *, user_id: int, date: datetime) -> Optional[DailyUserActivity]:
        """Get daily activity for a specific user and date"""
        date_only = date.date()
        statement = (
            select(DailyUserActivity)
            .where(and_(
                DailyUserActivity.user_id == user_id,
                DailyUserActivity.date == date_only
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_user_activity_range(self, db: AsyncSession, *, user_id: int, 
                                    start_date: datetime, end_date: datetime) -> List[DailyUserActivity]:
        """Get user activity within a date range"""
        statement = (
            select(DailyUserActivity)
            .where(and_(
                DailyUserActivity.user_id == user_id,
                DailyUserActivity.date >= start_date.date(),
                DailyUserActivity.date <= end_date.date()
            ))
            .order_by(asc(DailyUserActivity.date))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_most_active_users(self, db: AsyncSession, *, days: int = 7, limit: int = 10) -> List[Tuple[int, int]]:
        """Get most active users in the last N days"""
        since_date = datetime.utcnow().date() - timedelta(days=days)
        statement = (
            select(
                DailyUserActivity.user_id,
                func.sum(DailyUserActivity.questions_attempted).label('total_questions')
            )
            .where(DailyUserActivity.date >= since_date)
            .group_by(DailyUserActivity.user_id)
            .order_by(desc('total_questions'))
            .limit(limit)
        )
        result = await db.execute(statement)
        return [(row[0], row[1]) for row in result.all()]
    
    async def get_activity_trends(self, db: AsyncSession, *, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get activity trends for a user"""
        since_date = datetime.utcnow().date() - timedelta(days=days)
        statement = (
            select(
                func.avg(DailyUserActivity.questions_attempted).label('avg_questions'),
                func.max(DailyUserActivity.questions_attempted).label('max_questions'),
                func.avg(DailyUserActivity.correct_answers).label('avg_correct'),
                func.avg(DailyUserActivity.study_time_minutes).label('avg_study_time'),
                func.count(DailyUserActivity.id).label('active_days')
            )
            .where(and_(
                DailyUserActivity.user_id == user_id,
                DailyUserActivity.date >= since_date
            ))
        )
        result = await db.execute(statement)
        stats = result.first()
        
        return {
            "average_questions_per_day": float(stats.avg_questions or 0),
            "max_questions_in_day": int(stats.max_questions or 0),
            "average_correct_per_day": float(stats.avg_correct or 0),
            "average_study_time_minutes": float(stats.avg_study_time or 0),
            "active_days": int(stats.active_days or 0),
            "activity_rate": (int(stats.active_days or 0) / days) * 100
        }

class WeeklyUserActivityRepository(BaseRepository[WeeklyUserActivity, WeeklyUserActivityCreate, WeeklyUserActivityUpdate]):
    
    async def get_by_user_and_week(self, db: AsyncSession, *, user_id: int, year: int, week: int) -> Optional[WeeklyUserActivity]:
        """Get weekly activity for a specific user, year, and week"""
        statement = (
            select(WeeklyUserActivity)
            .where(and_(
                WeeklyUserActivity.user_id == user_id,
                WeeklyUserActivity.year == year,
                WeeklyUserActivity.week_number == week
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_user_weekly_trends(self, db: AsyncSession, *, user_id: int, weeks: int = 12) -> List[WeeklyUserActivity]:
        """Get weekly trends for a user"""
        statement = (
            select(WeeklyUserActivity)
            .where(WeeklyUserActivity.user_id == user_id)
            .order_by(desc(WeeklyUserActivity.year), desc(WeeklyUserActivity.week_number))
            .limit(weeks)
        )
        result = await db.execute(statement)
        return result.scalars().all()

class MonthlyUserActivityRepository(BaseRepository[MonthlyUserActivity, MonthlyUserActivityCreate, MonthlyUserActivityUpdate]):
    
    async def get_by_user_and_month(self, db: AsyncSession, *, user_id: int, year: int, month: int) -> Optional[MonthlyUserActivity]:
        """Get monthly activity for a specific user, year, and month"""
        statement = (
            select(MonthlyUserActivity)
            .where(and_(
                MonthlyUserActivity.user_id == user_id,
                MonthlyUserActivity.year == year,
                MonthlyUserActivity.month == month
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

class SubjectPerformanceAnalyticsRepository(BaseRepository[SubjectPerformanceAnalytics, SubjectPerformanceAnalyticsCreate, SubjectPerformanceAnalyticsUpdate]):
    
    async def get_by_user_and_subject(self, db: AsyncSession, *, user_id: int, subject_id: int) -> Optional[SubjectPerformanceAnalytics]:
        """Get performance analytics for a specific user and subject"""
        statement = (
            select(SubjectPerformanceAnalytics)
            .where(and_(
                SubjectPerformanceAnalytics.user_id == user_id,
                SubjectPerformanceAnalytics.subject_id == subject_id
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_user_subject_performance(self, db: AsyncSession, *, user_id: int) -> List[SubjectPerformanceAnalytics]:
        """Get performance analytics for all subjects for a user"""
        statement = (
            select(SubjectPerformanceAnalytics)
            .options(joinedload(SubjectPerformanceAnalytics.subject))
            .where(SubjectPerformanceAnalytics.user_id == user_id)
            .order_by(desc(SubjectPerformanceAnalytics.accuracy_rate))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_top_performing_subjects(self, db: AsyncSession, *, user_id: int, limit: int = 5) -> List[SubjectPerformanceAnalytics]:
        """Get top performing subjects for a user"""
        statement = (
            select(SubjectPerformanceAnalytics)
            .options(joinedload(SubjectPerformanceAnalytics.subject))
            .where(SubjectPerformanceAnalytics.user_id == user_id)
            .order_by(desc(SubjectPerformanceAnalytics.accuracy_rate))
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_subjects_needing_attention(self, db: AsyncSession, *, user_id: int, 
                                          accuracy_threshold: float = 60.0) -> List[SubjectPerformanceAnalytics]:
        """Get subjects with low performance that need attention"""
        statement = (
            select(SubjectPerformanceAnalytics)
            .options(joinedload(SubjectPerformanceAnalytics.subject))
            .where(and_(
                SubjectPerformanceAnalytics.user_id == user_id,
                SubjectPerformanceAnalytics.accuracy_rate < accuracy_threshold,
                SubjectPerformanceAnalytics.total_attempts >= 5  # Minimum attempts for meaningful data
            ))
            .order_by(asc(SubjectPerformanceAnalytics.accuracy_rate))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def calculate_subject_performance(self, db: AsyncSession, *, user_id: int, subject_id: int) -> Dict[str, Any]:
        """Calculate real-time performance metrics for a subject"""
        statement = (
            select(
                func.count(UserAttempt.id).label('total_attempts'),
                func.sum(case((UserAttempt.is_correct == True, 1), else_=0)).label('correct_attempts'),
                func.avg(UserAttempt.time_taken).label('avg_time'),
                func.avg(UserAttempt.confidence_level).label('avg_confidence'),
                func.count(func.distinct(UserAttempt.question_id)).label('unique_questions')
            )
            .join(Question)
            .where(and_(
                UserAttempt.user_id == user_id,
                Question.subject_id == subject_id
            ))
        )
        result = await db.execute(statement)
        stats = result.first()
        
        total = stats.total_attempts or 0
        correct = stats.correct_attempts or 0
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy_rate": accuracy,
            "average_time_per_question": float(stats.avg_time or 0),
            "average_confidence": float(stats.avg_confidence or 0),
            "unique_questions_attempted": stats.unique_questions or 0
        }

class TopicPerformanceAnalyticsRepository(BaseRepository[TopicPerformanceAnalytics, TopicPerformanceAnalyticsCreate, TopicPerformanceAnalyticsUpdate]):
    
    async def get_by_user_and_topic(self, db: AsyncSession, *, user_id: int, topic_id: int) -> Optional[TopicPerformanceAnalytics]:
        """Get performance analytics for a specific user and topic"""
        statement = (
            select(TopicPerformanceAnalytics)
            .where(and_(
                TopicPerformanceAnalytics.user_id == user_id,
                TopicPerformanceAnalytics.topic_id == topic_id
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_subject_topic_performance(self, db: AsyncSession, *, user_id: int, subject_id: int) -> List[TopicPerformanceAnalytics]:
        """Get performance analytics for all topics in a subject"""
        statement = (
            select(TopicPerformanceAnalytics)
            .join(Topic)
            .options(joinedload(TopicPerformanceAnalytics.topic))
            .where(and_(
                TopicPerformanceAnalytics.user_id == user_id,
                Topic.subject_id == subject_id
            ))
            .order_by(desc(TopicPerformanceAnalytics.accuracy_rate))
        )
        result = await db.execute(statement)
        return result.scalars().all()

class DifficultyLevelAnalyticsRepository(BaseRepository[DifficultyLevelAnalytics, DifficultyLevelAnalyticsCreate, DifficultyLevelAnalyticsUpdate]):
    
    async def get_by_user_and_difficulty(self, db: AsyncSession, *, user_id: int, difficulty_level: str) -> Optional[DifficultyLevelAnalytics]:
        """Get analytics for a specific difficulty level"""
        statement = (
            select(DifficultyLevelAnalytics)
            .where(and_(
                DifficultyLevelAnalytics.user_id == user_id,
                DifficultyLevelAnalytics.difficulty_level == difficulty_level
            ))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_user_difficulty_progression(self, db: AsyncSession, *, user_id: int) -> List[DifficultyLevelAnalytics]:
        """Get difficulty progression for a user"""
        statement = (
            select(DifficultyLevelAnalytics)
            .where(DifficultyLevelAnalytics.user_id == user_id)
            .order_by(DifficultyLevelAnalytics.difficulty_level)
        )
        result = await db.execute(statement)
        return result.scalars().all()

class LearningPathAnalyticsRepository(BaseRepository[LearningPathAnalytics, LearningPathAnalyticsCreate, LearningPathAnalyticsUpdate]):
    
    async def get_by_user(self, db: AsyncSession, *, user_id: int) -> List[LearningPathAnalytics]:
        """Get learning path analytics for a user"""
        return await self.get_multi_by_attribute(db, attribute="user_id", value=user_id)
    
    async def get_current_learning_paths(self, db: AsyncSession, *, user_id: int) -> List[LearningPathAnalytics]:
        """Get current active learning paths for a user"""
        statement = (
            select(LearningPathAnalytics)
            .where(and_(
                LearningPathAnalytics.user_id == user_id,
                LearningPathAnalytics.is_completed == False
            ))
            .order_by(desc(LearningPathAnalytics.created_at))
        )
        result = await db.execute(statement)
        return result.scalars().all()

class AnalyticsRepository:
    """Aggregate repository for analytics operations"""
    
    def __init__(self):
        self.daily_activity = DailyUserActivityRepository(DailyUserActivity)
        self.weekly_activity = WeeklyUserActivityRepository(WeeklyUserActivity)
        self.monthly_activity = MonthlyUserActivityRepository(MonthlyUserActivity)
        self.subject_performance = SubjectPerformanceAnalyticsRepository(SubjectPerformanceAnalytics)
        self.topic_performance = TopicPerformanceAnalyticsRepository(TopicPerformanceAnalytics)
        self.difficulty_analytics = DifficultyLevelAnalyticsRepository(DifficultyLevelAnalytics)
        self.learning_path = LearningPathAnalyticsRepository(LearningPathAnalytics)
    
    async def get_user_dashboard_data(self, db: AsyncSession, *, user_id: int) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        # Get activity trends
        activity_trends = await self.daily_activity.get_activity_trends(db, user_id=user_id, days=30)
        
        # Get subject performance
        subject_performance = await self.subject_performance.get_user_subject_performance(db, user_id=user_id)
        
        # Get subjects needing attention
        attention_subjects = await self.subject_performance.get_subjects_needing_attention(db, user_id=user_id)
        
        # Get difficulty progression
        difficulty_progression = await self.difficulty_analytics.get_user_difficulty_progression(db, user_id=user_id)
        
        # Get current learning paths
        learning_paths = await self.learning_path.get_current_learning_paths(db, user_id=user_id)
        
        # Recent activity (last 7 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        recent_activity = await self.daily_activity.get_user_activity_range(
            db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        
        return {
            "activity_trends": activity_trends,
            "subject_performance": [
                {
                    "subject_name": perf.subject.name if perf.subject else "Unknown",
                    "accuracy_rate": perf.accuracy_rate,
                    "total_attempts": perf.total_attempts,
                    "average_time": perf.average_time_per_question,
                    "improvement_rate": perf.improvement_rate
                }
                for perf in subject_performance
            ],
            "subjects_needing_attention": [
                {
                    "subject_name": subj.subject.name if subj.subject else "Unknown",
                    "accuracy_rate": subj.accuracy_rate,
                    "total_attempts": subj.total_attempts
                }
                for subj in attention_subjects
            ],
            "difficulty_progression": [
                {
                    "difficulty": diff.difficulty_level,
                    "accuracy": diff.accuracy_rate,
                    "attempts": diff.total_attempts
                }
                for diff in difficulty_progression
            ],
            "active_learning_paths": len(learning_paths),
            "recent_activity": [
                {
                    "date": str(activity.date),
                    "questions_attempted": activity.questions_attempted,
                    "correct_answers": activity.correct_answers,
                    "study_time": activity.study_time_minutes
                }
                for activity in recent_activity
            ]
        }
    
    async def generate_performance_insights(self, db: AsyncSession, *, user_id: int) -> Dict[str, Any]:
        """Generate AI-powered insights about user performance"""
        # Get comprehensive performance data
        subject_performance = await self.subject_performance.get_user_subject_performance(db, user_id=user_id)
        difficulty_progression = await self.difficulty_analytics.get_user_difficulty_progression(db, user_id=user_id)
        activity_trends = await self.daily_activity.get_activity_trends(db, user_id=user_id, days=30)
        
        insights = []
        
        # Activity insights
        if activity_trends["activity_rate"] < 50:
            insights.append({
                "type": "activity",
                "priority": "high",
                "message": "Your study consistency could be improved. Try to practice a little each day.",
                "recommendation": "Set a daily practice goal of at least 10 questions."
            })
        
        # Subject performance insights
        if subject_performance:
            best_subject = max(subject_performance, key=lambda x: x.accuracy_rate)
            worst_subject = min(subject_performance, key=lambda x: x.accuracy_rate)
            
            if best_subject.accuracy_rate - worst_subject.accuracy_rate > 30:
                insights.append({
                    "type": "subject_balance",
                    "priority": "medium",
                    "message": f"Large performance gap between {best_subject.subject.name if best_subject.subject else 'best'} and {worst_subject.subject.name if worst_subject.subject else 'worst'} subjects.",
                    "recommendation": f"Focus more practice time on {worst_subject.subject.name if worst_subject.subject else 'weaker subjects'}."
                })
        
        # Difficulty progression insights
        if difficulty_progression:
            easy_performance = next((d for d in difficulty_progression if d.difficulty_level == "EASY"), None)
            hard_performance = next((d for d in difficulty_progression if d.difficulty_level == "HARD"), None)
            
            if easy_performance and easy_performance.accuracy_rate > 80 and (not hard_performance or hard_performance.total_attempts < 10):
                insights.append({
                    "type": "difficulty_progression",
                    "priority": "medium",
                    "message": "You're performing well on easy questions. Consider challenging yourself with harder questions.",
                    "recommendation": "Try more medium and hard difficulty questions to accelerate learning."
                })
        
        return {
            "insights": insights,
            "overall_score": self._calculate_overall_score(activity_trends, subject_performance, difficulty_progression),
            "next_steps": self._generate_next_steps(subject_performance, difficulty_progression)
        }
    
    def _calculate_overall_score(self, activity_trends: Dict, subject_performance: List, difficulty_progression: List) -> float:
        """Calculate an overall performance score (0-100)"""
        activity_score = min(activity_trends["activity_rate"], 100) * 0.3
        
        if subject_performance:
            avg_accuracy = sum(s.accuracy_rate for s in subject_performance) / len(subject_performance)
            performance_score = avg_accuracy * 0.5
        else:
            performance_score = 0
        
        consistency_score = (activity_trends["activity_rate"]) * 0.2
        
        return min(activity_score + performance_score + consistency_score, 100)
    
    def _generate_next_steps(self, subject_performance: List, difficulty_progression: List) -> List[str]:
        """Generate personalized next steps"""
        steps = []
        
        if not subject_performance:
            steps.append("Start practicing questions to build your performance profile.")
            return steps
        
        # Find weakest subject
        weakest = min(subject_performance, key=lambda x: x.accuracy_rate)
        if weakest.accuracy_rate < 70:
            steps.append(f"Focus on improving {weakest.subject.name if weakest.subject else 'weak subject'} - current accuracy: {weakest.accuracy_rate:.1f}%")
        
        # Check for difficulty progression
        easy_perf = next((d for d in difficulty_progression if d.difficulty_level == "EASY"), None)
        if easy_perf and easy_perf.accuracy_rate > 80:
            steps.append("Challenge yourself with medium and hard difficulty questions")
        
        steps.append("Maintain consistent daily practice for best results")
        
        return steps

# Initialize repository instances
analytics_repo = AnalyticsRepository()
daily_activity_repo = DailyUserActivityRepository(DailyUserActivity)
weekly_activity_repo = WeeklyUserActivityRepository(WeeklyUserActivity)
monthly_activity_repo = MonthlyUserActivityRepository(MonthlyUserActivity)
subject_performance_repo = SubjectPerformanceAnalyticsRepository(SubjectPerformanceAnalytics)
topic_performance_repo = TopicPerformanceAnalyticsRepository(TopicPerformanceAnalytics)
difficulty_analytics_repo = DifficultyLevelAnalyticsRepository(DifficultyLevelAnalytics)
learning_path_repo = LearningPathAnalyticsRepository(LearningPathAnalytics)
