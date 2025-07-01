from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from datetime import datetime, timedelta, date
import logging

from app.models.analytics import (
    UserAnalytics, LearningAnalytics, QuestionAnalytics, SystemAnalytics,
    UserEvent, PerformanceTrend, DailyUserActivity, WeeklyUserActivity,
    MonthlyUserActivity, SubjectPerformanceAnalytics, TopicPerformanceAnalytics,
    DifficultyLevelAnalytics, LearningPathAnalytics, EventType, PerformanceLevel
)
from app.models.practice import PracticeSession, UserAttempt
from app.models.user import User
from app.schemas.analytics import (
    UserAnalyticsCreate, UserAnalyticsUpdate,
    LearningAnalyticsCreate, LearningAnalyticsUpdate,
    UserEventCreate, PerformanceTrendCreate,
    DashboardQuery, ReportQuery, AnalyticsExport
)
from app.services.base import BaseService

logger = logging.getLogger(__name__)

class AnalyticsService(BaseService[UserAnalytics, UserAnalyticsCreate, UserAnalyticsUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserAnalytics, db)
    
    async def get_user_analytics(self, user_id: int) -> Optional[UserAnalytics]:
        """Get user analytics data"""
        try:
            query = select(UserAnalytics).where(UserAnalytics.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user analytics for {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update_user_analytics(self, user_id: int, session: PracticeSession):
        """Update user analytics after a practice session"""
        try:
            # Get or create user analytics
            analytics = await self.get_user_analytics(user_id)
            
            if not analytics:
                analytics = UserAnalytics(user_id=user_id)
                self.db.add(analytics)
            
            # Update analytics
            analytics.total_questions_attempted += session.total_questions or 0
            analytics.correct_answers += session.correct_answers or 0
            analytics.incorrect_answers += session.incorrect_answers or 0
            analytics.total_practice_sessions += 1
            
            if session.total_time_spent:
                analytics.total_study_time += session.total_time_spent
            
            if session.score_percentage:
                # Update average score (weighted average)
                total_sessions = analytics.total_practice_sessions
                current_avg = analytics.average_score or 0
                analytics.average_score = ((current_avg * (total_sessions - 1)) + session.score_percentage) / total_sessions
            
            # Update accuracy rate
            total_answered = analytics.correct_answers + analytics.incorrect_answers
            if total_answered > 0:
                analytics.overall_accuracy_rate = (analytics.correct_answers / total_answered) * 100
            
            # Update streak
            if session.score_percentage and session.score_percentage >= 70:  # Consider 70% as a good session
                analytics.current_streak += 1
                if analytics.current_streak > analytics.best_streak:
                    analytics.best_streak = analytics.current_streak
            else:
                analytics.current_streak = 0
            
            analytics.last_activity_date = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(analytics)
            
            # Update daily activity
            await self._update_daily_activity(user_id, session)
            
            return analytics
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user analytics: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def track_user_event(self, user_id: int, event_data: UserEventCreate) -> UserEvent:
        """Track a user event"""
        try:
            event_dict = event_data.dict()
            event_dict["user_id"] = user_id
            event_dict["timestamp"] = datetime.utcnow()
            
            event = UserEvent(**event_dict)
            self.db.add(event)
            await self.db.commit()
            await self.db.refresh(event)
            return event
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error tracking user event: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_user_dashboard_data(self, user_id: int, query: DashboardQuery) -> Dict[str, Any]:
        """Get dashboard data for a user"""
        try:
            # Get user analytics
            analytics = await self.get_user_analytics(user_id)
            
            # Get recent sessions
            recent_sessions_query = select(PracticeSession).where(
                PracticeSession.user_id == user_id
            ).order_by(desc(PracticeSession.created_at)).limit(5)
            
            recent_sessions_result = await self.db.execute(recent_sessions_query)
            recent_sessions = recent_sessions_result.scalars().all()
            
            # Get weekly progress
            weekly_data = await self._get_weekly_progress(user_id, query.days_back or 7)
            
            # Get subject performance
            subject_performance = await self._get_subject_performance(user_id)
            
            # Get learning trends
            learning_trends = await self._get_learning_trends(user_id, query.days_back or 30)
            
            return {
                "user_analytics": analytics,
                "recent_sessions": recent_sessions,
                "weekly_progress": weekly_data,
                "subject_performance": subject_performance,
                "learning_trends": learning_trends,
                "performance_level": self._calculate_performance_level(analytics),
                "recommendations": await self._get_recommendations(user_id)
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_performance_trends(self, user_id: int, days: int = 30) -> List[PerformanceTrend]:
        """Get performance trends for a user"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(PerformanceTrend).where(
                and_(
                    PerformanceTrend.user_id == user_id,
                    PerformanceTrend.period_start >= cutoff_date
                )
            ).order_by(PerformanceTrend.period_start)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting performance trends: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def generate_analytics_report(self, query: ReportQuery) -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            report_data = {
                "report_type": query.report_type,
                "period": {"start": query.start_date, "end": query.end_date},
                "generated_at": datetime.utcnow()
            }
            
            if query.report_type == "user_performance":
                report_data.update(await self._generate_user_performance_report(query))
            elif query.report_type == "question_analytics":
                report_data.update(await self._generate_question_analytics_report(query))
            elif query.report_type == "system_usage":
                report_data.update(await self._generate_system_usage_report(query))
            elif query.report_type == "learning_progress":
                report_data.update(await self._generate_learning_progress_report(query))
            
            return report_data
        except Exception as e:
            logger.error(f"Error generating analytics report: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def _update_daily_activity(self, user_id: int, session: PracticeSession):
        """Update daily user activity"""
        try:
            today = date.today()
            
            # Get or create daily activity record
            activity_query = select(DailyUserActivity).where(
                and_(
                    DailyUserActivity.user_id == user_id,
                    DailyUserActivity.date == today
                )
            )
            activity_result = await self.db.execute(activity_query)
            activity = activity_result.scalar_one_or_none()
            
            if not activity:
                activity = DailyUserActivity(user_id=user_id, date=today)
                self.db.add(activity)
            
            # Update activity metrics
            activity.questions_attempted += session.total_questions or 0
            activity.correct_answers += session.correct_answers or 0
            activity.incorrect_answers += session.incorrect_answers or 0
            activity.sessions_completed += 1
            
            if session.total_time_spent:
                activity.study_time_minutes += session.total_time_spent
            
            # Recalculate accuracy rate
            total_answered = activity.correct_answers + activity.incorrect_answers
            if total_answered > 0:
                activity.accuracy_rate = (activity.correct_answers / total_answered) * 100
            
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error updating daily activity: {str(e)}")
    
    async def _get_weekly_progress(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """Get weekly progress data"""
        try:
            cutoff_date = date.today() - timedelta(days=days)
            
            query = select(DailyUserActivity).where(
                and_(
                    DailyUserActivity.user_id == user_id,
                    DailyUserActivity.date >= cutoff_date
                )
            ).order_by(DailyUserActivity.date)
            
            result = await self.db.execute(query)
            daily_activities = result.scalars().all()
            
            return [
                {
                    "date": activity.date.isoformat(),
                    "questions_attempted": activity.questions_attempted,
                    "accuracy_rate": activity.accuracy_rate,
                    "study_time": activity.study_time_minutes
                }
                for activity in daily_activities
            ]
        except Exception as e:
            logger.error(f"Error getting weekly progress: {str(e)}")
            return []
    
    async def _get_subject_performance(self, user_id: int) -> List[Dict[str, Any]]:
        """Get subject performance data"""
        try:
            query = select(SubjectPerformanceAnalytics).options(
                selectinload(SubjectPerformanceAnalytics.subject)
            ).where(SubjectPerformanceAnalytics.user_id == user_id)
            
            result = await self.db.execute(query)
            performance_data = result.scalars().all()
            
            return [
                {
                    "subject_name": perf.subject.name if perf.subject else "Unknown",
                    "total_attempts": perf.total_attempts,
                    "accuracy_rate": perf.accuracy_rate,
                    "improvement_rate": perf.improvement_rate
                }
                for perf in performance_data
            ]
        except Exception as e:
            logger.error(f"Error getting subject performance: {str(e)}")
            return []
    
    async def _get_learning_trends(self, user_id: int, days: int) -> Dict[str, Any]:
        """Get learning trends"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get sessions in the period
            sessions_query = select(PracticeSession).where(
                and_(
                    PracticeSession.user_id == user_id,
                    PracticeSession.created_at >= cutoff_date
                )
            )
            
            sessions_result = await self.db.execute(sessions_query)
            sessions = sessions_result.scalars().all()
            
            if not sessions:
                return {"trend": "no_data", "sessions_count": 0}
            
            # Calculate trend
            scores = [s.score_percentage for s in sessions if s.score_percentage is not None]
            if len(scores) < 2:
                return {"trend": "insufficient_data", "sessions_count": len(sessions)}
            
            # Simple trend calculation
            mid_point = len(scores) // 2
            first_half_avg = sum(scores[:mid_point]) / mid_point
            second_half_avg = sum(scores[mid_point:]) / (len(scores) - mid_point)
            
            trend = "improving" if second_half_avg > first_half_avg else "declining"
            improvement = second_half_avg - first_half_avg
            
            return {
                "trend": trend,
                "improvement_percentage": improvement,
                "sessions_count": len(sessions),
                "average_score": sum(scores) / len(scores)
            }
        except Exception as e:
            logger.error(f"Error getting learning trends: {str(e)}")
            return {"trend": "error", "sessions_count": 0}
    
    def _calculate_performance_level(self, analytics: Optional[UserAnalytics]) -> str:
        """Calculate user performance level"""
        if not analytics:
            return PerformanceLevel.BEGINNER.value
        
        accuracy = analytics.overall_accuracy_rate or 0
        sessions = analytics.total_practice_sessions or 0
        
        if accuracy >= 85 and sessions >= 50:
            return PerformanceLevel.EXPERT.value
        elif accuracy >= 75 and sessions >= 25:
            return PerformanceLevel.ADVANCED.value
        elif accuracy >= 60 and sessions >= 10:
            return PerformanceLevel.INTERMEDIATE.value
        else:
            return PerformanceLevel.BEGINNER.value
    
    async def _get_recommendations(self, user_id: int) -> List[str]:
        """Get personalized recommendations"""
        try:
            analytics = await self.get_user_analytics(user_id)
            recommendations = []
            
            if not analytics:
                return ["Start practicing to get personalized recommendations!"]
            
            # Accuracy-based recommendations
            if analytics.overall_accuracy_rate and analytics.overall_accuracy_rate < 60:
                recommendations.append("Focus on reviewing fundamental concepts")
                recommendations.append("Try easier questions to build confidence")
            elif analytics.overall_accuracy_rate and analytics.overall_accuracy_rate > 85:
                recommendations.append("Challenge yourself with harder questions")
                recommendations.append("Explore advanced topics")
            
            # Study time recommendations
            if analytics.total_study_time and analytics.total_study_time < 300:  # Less than 5 hours
                recommendations.append("Increase your study time for better results")
            
            # Streak recommendations
            if analytics.current_streak == 0:
                recommendations.append("Start a new practice streak today!")
            elif analytics.current_streak > 0 and analytics.current_streak < 7:
                recommendations.append(f"Keep going! You're on a {analytics.current_streak}-day streak")
            
            return recommendations[:3]  # Return top 3 recommendations
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return ["Unable to generate recommendations at this time"]
    
    async def _generate_user_performance_report(self, query: ReportQuery) -> Dict[str, Any]:
        """Generate user performance report"""
        # Implementation would go here
        return {"report_data": "user_performance_placeholder"}
    
    async def _generate_question_analytics_report(self, query: ReportQuery) -> Dict[str, Any]:
        """Generate question analytics report"""
        # Implementation would go here
        return {"report_data": "question_analytics_placeholder"}
    
    async def _generate_system_usage_report(self, query: ReportQuery) -> Dict[str, Any]:
        """Generate system usage report"""
        # Implementation would go here
        return {"report_data": "system_usage_placeholder"}
    
    async def _generate_learning_progress_report(self, query: ReportQuery) -> Dict[str, Any]:
        """Generate learning progress report"""
        # Implementation would go here
        return {"report_data": "learning_progress_placeholder"}
