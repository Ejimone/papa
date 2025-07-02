"""
Analytics background tasks for data aggregation, reporting, and insights generation.
Handles periodic analytics calculations and report generation.
"""

import asyncio
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from celery import current_task
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models import (
    User, Question, UserAttempt, PracticeSession, UserAnalytics,
    DailyUserActivity, WeeklyUserActivity, MonthlyUserActivity,
    Subject, Topic, QuestionAnalytics, SystemAnalytics
)
from app.services.analytics_service import AnalyticsService
from app.core.logging import get_logger

logger = get_logger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def aggregate_daily_analytics(self):
    """Aggregate daily analytics for all users"""
    try:
        return asyncio.run(_aggregate_daily_analytics())
    except Exception as exc:
        logger.error(f"Daily analytics aggregation failed: {exc}")
        raise self.retry(exc=exc)

async def _aggregate_daily_analytics():
    """Internal async function for daily analytics aggregation"""
    async with AsyncSessionLocal() as db:
        try:
            analytics_service = AnalyticsService(db)
            yesterday = date.today() - timedelta(days=1)
            
            # Get all active users
            result = await db.execute(
                "SELECT id FROM users WHERE is_active = true"
            )
            user_ids = [row[0] for row in result.fetchall()]
            
            processed_count = 0
            for user_id in user_ids:
                try:
                    # Aggregate user's daily activity
                    await _aggregate_user_daily_activity(db, user_id, yesterday)
                    processed_count += 1
                    
                    # Update task progress
                    if current_task:
                        current_task.update_state(
                            state='PROGRESS',
                            meta={'current': processed_count, 'total': len(user_ids)}
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to aggregate daily analytics for user {user_id}: {e}")
                    continue
            
            await db.commit()
            
            logger.info(f"Successfully aggregated daily analytics for {processed_count}/{len(user_ids)} users")
            return {
                "status": "success",
                "date": yesterday.isoformat(),
                "users_processed": processed_count,
                "total_users": len(user_ids)
            }
            
        except Exception as e:
            await db.rollback()
            raise e

async def _aggregate_user_daily_activity(db: AsyncSession, user_id: int, target_date: date):
    """Aggregate daily activity for a specific user"""
    from sqlalchemy import text
    
    # Calculate daily metrics
    query = text("""
        SELECT 
            COUNT(DISTINCT ua.id) as questions_attempted,
            COUNT(CASE WHEN ua.is_correct = true THEN 1 END) as correct_answers,
            COALESCE(SUM(ua.time_taken), 0) as total_time,
            COUNT(DISTINCT ps.id) as sessions_completed
        FROM user_attempts ua
        LEFT JOIN practice_sessions ps ON ua.session_id = ps.id
        WHERE ua.user_id = :user_id 
        AND DATE(ua.created_at) = :target_date
    """)
    
    result = await db.execute(query, {"user_id": user_id, "target_date": target_date})
    row = result.fetchone()
    
    if row and row[0] > 0:  # Only create record if user had activity
        questions_attempted = row[0] or 0
        correct_answers = row[1] or 0
        total_time = row[2] or 0
        sessions_completed = row[3] or 0
        
        accuracy_rate = (correct_answers / questions_attempted * 100) if questions_attempted > 0 else 0
        
        # Create or update daily activity record
        from app.models.analytics import DailyUserActivity
        
        daily_activity = DailyUserActivity(
            user_id=user_id,
            date=target_date,
            questions_attempted=questions_attempted,
            correct_answers=correct_answers,
            study_time_minutes=int(total_time / 60),  # Convert seconds to minutes
            sessions_completed=sessions_completed,
            accuracy_rate=accuracy_rate
        )
        
        db.add(daily_activity)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def aggregate_weekly_analytics(self):
    """Aggregate weekly analytics"""
    try:
        return asyncio.run(_aggregate_weekly_analytics())
    except Exception as exc:
        logger.error(f"Weekly analytics aggregation failed: {exc}")
        raise self.retry(exc=exc)

async def _aggregate_weekly_analytics():
    """Internal async function for weekly analytics aggregation"""
    async with AsyncSessionLocal() as db:
        try:
            # Calculate last week's date range
            today = date.today()
            last_week_start = today - timedelta(days=today.weekday() + 7)
            last_week_end = last_week_start + timedelta(days=6)
            
            year = last_week_start.year
            week_number = last_week_start.isocalendar()[1]
            
            # Get all active users
            from sqlalchemy import text
            result = await db.execute(text("SELECT id FROM users WHERE is_active = true"))
            user_ids = [row[0] for row in result.fetchall()]
            
            processed_count = 0
            for user_id in user_ids:
                try:
                    await _aggregate_user_weekly_activity(db, user_id, year, week_number, last_week_start, last_week_end)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Failed to aggregate weekly analytics for user {user_id}: {e}")
                    continue
            
            await db.commit()
            
            return {
                "status": "success",
                "week": f"{year}-W{week_number:02d}",
                "users_processed": processed_count,
                "total_users": len(user_ids)
            }
            
        except Exception as e:
            await db.rollback()
            raise e

async def _aggregate_user_weekly_activity(db: AsyncSession, user_id: int, year: int, week_number: int, start_date: date, end_date: date):
    """Aggregate weekly activity for a specific user"""
    from sqlalchemy import text
    
    # Aggregate from daily activities
    query = text("""
        SELECT 
            COALESCE(SUM(questions_attempted), 0) as total_questions,
            COALESCE(SUM(correct_answers), 0) as total_correct,
            COALESCE(SUM(study_time_minutes), 0) as total_time,
            COALESCE(SUM(sessions_completed), 0) as total_sessions
        FROM daily_user_activities
        WHERE user_id = :user_id 
        AND date BETWEEN :start_date AND :end_date
    """)
    
    result = await db.execute(query, {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date
    })
    row = result.fetchone()
    
    if row and row[0] > 0:  # Only create record if user had activity
        questions_attempted = row[0] or 0
        correct_answers = row[1] or 0
        study_time = row[2] or 0
        sessions_completed = row[3] or 0
        
        accuracy_rate = (correct_answers / questions_attempted * 100) if questions_attempted > 0 else 0
        
        from app.models.analytics import WeeklyUserActivity
        
        weekly_activity = WeeklyUserActivity(
            user_id=user_id,
            year=year,
            week_number=week_number,
            questions_attempted=questions_attempted,
            correct_answers=correct_answers,
            study_time_minutes=study_time,
            sessions_completed=sessions_completed,
            accuracy_rate=accuracy_rate
        )
        
        db.add(weekly_activity)

@celery_app.task(bind=True, max_retries=3)
def update_question_analytics(self):
    """Update analytics for all questions"""
    try:
        return asyncio.run(_update_question_analytics())
    except Exception as exc:
        logger.error(f"Question analytics update failed: {exc}")
        raise self.retry(exc=exc)

async def _update_question_analytics():
    """Update question performance analytics"""
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import text
            
            # Get questions that need analytics updates
            query = text("""
                SELECT DISTINCT q.id 
                FROM questions q
                INNER JOIN user_attempts ua ON q.id = ua.question_id
                WHERE ua.created_at >= NOW() - INTERVAL '2 hours'
            """)
            
            result = await db.execute(query)
            question_ids = [row[0] for row in result.fetchall()]
            
            updated_count = 0
            for question_id in question_ids:
                try:
                    await _update_single_question_analytics(db, question_id)
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to update analytics for question {question_id}: {e}")
                    continue
            
            await db.commit()
            
            return {
                "status": "success",
                "questions_updated": updated_count,
                "total_questions": len(question_ids)
            }
            
        except Exception as e:
            await db.rollback()
            raise e

async def _update_single_question_analytics(db: AsyncSession, question_id: int):
    """Update analytics for a single question"""
    from sqlalchemy import text
    
    # Calculate question metrics
    query = text("""
        SELECT 
            COUNT(*) as total_attempts,
            COUNT(CASE WHEN is_correct = true THEN 1 END) as correct_attempts,
            COUNT(DISTINCT user_id) as unique_users,
            AVG(time_taken) as avg_time,
            COUNT(CASE WHEN hint_used = true THEN 1 END) as hint_requests
        FROM user_attempts
        WHERE question_id = :question_id
        AND created_at >= CURRENT_DATE
    """)
    
    result = await db.execute(query, {"question_id": question_id})
    row = result.fetchone()
    
    if row and row[0] > 0:
        total_attempts = row[0] or 0
        correct_attempts = row[1] or 0
        unique_users = row[2] or 0
        avg_time = float(row[3] or 0)
        hint_requests = row[4] or 0
        
        success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Update or create question analytics
        from app.models.analytics import QuestionAnalytics
        
        analytics = QuestionAnalytics(
            question_id=question_id,
            date=date.today(),
            attempts_count=total_attempts,
            unique_users=unique_users,
            success_rate=success_rate,
            average_time=avg_time,
            hint_requests=hint_requests
        )
        
        db.add(analytics)

@celery_app.task(bind=True)
def generate_weekly_reports(self):
    """Generate weekly reports for users and administrators"""
    try:
        return asyncio.run(_generate_weekly_reports())
    except Exception as exc:
        logger.error(f"Weekly report generation failed: {exc}")
        raise self.retry(exc=exc)

async def _generate_weekly_reports():
    """Generate comprehensive weekly reports"""
    async with AsyncSessionLocal() as db:
        try:
            # Calculate last week's date range
            today = date.today()
            last_week_start = today - timedelta(days=today.weekday() + 7)
            last_week_end = last_week_start + timedelta(days=6)
            
            # Generate user reports
            user_reports = await _generate_user_weekly_reports(db, last_week_start, last_week_end)
            
            # Generate admin report
            admin_report = await _generate_admin_weekly_report(db, last_week_start, last_week_end)
            
            return {
                "status": "success",
                "period": f"{last_week_start} to {last_week_end}",
                "user_reports": len(user_reports),
                "admin_report": admin_report is not None
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly reports: {e}")
            raise e

async def _generate_user_weekly_reports(db: AsyncSession, start_date: date, end_date: date) -> List[Dict]:
    """Generate weekly reports for individual users"""
    from sqlalchemy import text
    
    # Get users with activity in the past week
    query = text("""
        SELECT DISTINCT u.id, u.email, u.full_name
        FROM users u
        INNER JOIN daily_user_activities dua ON u.id = dua.user_id
        WHERE dua.date BETWEEN :start_date AND :end_date
        AND u.is_active = true
    """)
    
    result = await db.execute(query, {"start_date": start_date, "end_date": end_date})
    users = result.fetchall()
    
    reports = []
    for user in users:
        user_id, email, full_name = user
        
        # Get user's weekly stats
        stats_query = text("""
            SELECT 
                SUM(questions_attempted) as total_questions,
                SUM(correct_answers) as total_correct,
                SUM(study_time_minutes) as total_time,
                SUM(sessions_completed) as total_sessions,
                AVG(accuracy_rate) as avg_accuracy
            FROM daily_user_activities
            WHERE user_id = :user_id 
            AND date BETWEEN :start_date AND :end_date
        """)
        
        stats_result = await db.execute(stats_query, {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        })
        stats = stats_result.fetchone()
        
        if stats and stats[0]:
            report = {
                "user_id": user_id,
                "email": email,
                "name": full_name,
                "period": f"{start_date} to {end_date}",
                "questions_attempted": stats[0] or 0,
                "correct_answers": stats[1] or 0,
                "study_time_hours": round((stats[2] or 0) / 60, 1),
                "sessions_completed": stats[3] or 0,
                "average_accuracy": round(stats[4] or 0, 1),
                "generated_at": datetime.utcnow().isoformat()
            }
            reports.append(report)
    
    return reports

async def _generate_admin_weekly_report(db: AsyncSession, start_date: date, end_date: date) -> Dict:
    """Generate weekly administrative report"""
    from sqlalchemy import text
    
    # System-wide statistics
    system_query = text("""
        SELECT 
            COUNT(DISTINCT dua.user_id) as active_users,
            SUM(dua.questions_attempted) as total_questions,
            SUM(dua.study_time_minutes) as total_study_time,
            AVG(dua.accuracy_rate) as system_accuracy
        FROM daily_user_activities dua
        WHERE dua.date BETWEEN :start_date AND :end_date
    """)
    
    result = await db.execute(system_query, {"start_date": start_date, "end_date": end_date})
    system_stats = result.fetchone()
    
    # New user registrations
    new_users_query = text("""
        SELECT COUNT(*) as new_users
        FROM users
        WHERE DATE(created_at) BETWEEN :start_date AND :end_date
    """)
    
    new_users_result = await db.execute(new_users_query, {"start_date": start_date, "end_date": end_date})
    new_users = new_users_result.fetchone()[0] or 0
    
    # Top subjects
    top_subjects_query = text("""
        SELECT s.name, COUNT(ua.id) as attempts
        FROM user_attempts ua
        INNER JOIN questions q ON ua.question_id = q.id
        INNER JOIN subjects s ON q.subject_id = s.id
        WHERE DATE(ua.created_at) BETWEEN :start_date AND :end_date
        GROUP BY s.id, s.name
        ORDER BY attempts DESC
        LIMIT 5
    """)
    
    top_subjects_result = await db.execute(top_subjects_query, {"start_date": start_date, "end_date": end_date})
    top_subjects = [{"subject": row[0], "attempts": row[1]} for row in top_subjects_result.fetchall()]
    
    return {
        "period": f"{start_date} to {end_date}",
        "active_users": system_stats[0] or 0,
        "total_questions_attempted": system_stats[1] or 0,
        "total_study_hours": round((system_stats[2] or 0) / 60, 1),
        "system_accuracy": round(system_stats[3] or 0, 1),
        "new_user_registrations": new_users,
        "top_subjects": top_subjects,
        "generated_at": datetime.utcnow().isoformat()
    }

@celery_app.task(bind=True)
def calculate_user_insights(self, user_id: int):
    """Calculate personalized insights for a specific user"""
    try:
        return asyncio.run(_calculate_user_insights(user_id))
    except Exception as exc:
        logger.error(f"User insights calculation failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)

async def _calculate_user_insights(user_id: int):
    """Calculate insights and recommendations for a user"""
    async with AsyncSessionLocal() as db:
        try:
            # Get user's performance over last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            
            from sqlalchemy import text
            
            # Performance trends
            trends_query = text("""
                SELECT 
                    date,
                    questions_attempted,
                    accuracy_rate,
                    study_time_minutes
                FROM daily_user_activities
                WHERE user_id = :user_id 
                AND date >= :start_date
                ORDER BY date
            """)
            
            result = await db.execute(trends_query, {"user_id": user_id, "start_date": thirty_days_ago})
            daily_data = result.fetchall()
            
            if not daily_data:
                return {"status": "no_data", "user_id": user_id}
            
            # Calculate insights
            insights = {
                "user_id": user_id,
                "period": f"{thirty_days_ago} to {date.today()}",
                "total_days_active": len(daily_data),
                "average_daily_questions": sum(row[1] for row in daily_data) / len(daily_data),
                "average_accuracy": sum(row[2] for row in daily_data) / len(daily_data),
                "total_study_time": sum(row[3] for row in daily_data),
                "consistency_score": _calculate_consistency_score(daily_data),
                "improvement_trend": _calculate_improvement_trend(daily_data),
                "recommendations": await _generate_recommendations(db, user_id, daily_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {"status": "success", "insights": insights}
            
        except Exception as e:
            logger.error(f"Error calculating insights for user {user_id}: {e}")
            raise e

def _calculate_consistency_score(daily_data: List) -> float:
    """Calculate how consistent the user's study pattern is"""
    if len(daily_data) < 7:
        return 0.0
    
    study_times = [row[3] for row in daily_data]  # study_time_minutes
    if not study_times:
        return 0.0
    
    # Calculate coefficient of variation (lower = more consistent)
    mean_time = sum(study_times) / len(study_times)
    if mean_time == 0:
        return 0.0
    
    variance = sum((x - mean_time) ** 2 for x in study_times) / len(study_times)
    std_dev = variance ** 0.5
    cv = std_dev / mean_time
    
    # Convert to 0-100 scale (lower CV = higher consistency score)
    consistency = max(0, 100 - (cv * 100))
    return round(consistency, 1)

def _calculate_improvement_trend(daily_data: List) -> str:
    """Calculate if user is improving, declining, or stable"""
    if len(daily_data) < 14:
        return "insufficient_data"
    
    # Split data into first and second half
    mid_point = len(daily_data) // 2
    first_half = daily_data[:mid_point]
    second_half = daily_data[mid_point:]
    
    # Compare average accuracy
    first_avg = sum(row[2] for row in first_half) / len(first_half)
    second_avg = sum(row[2] for row in second_half) / len(second_half)
    
    improvement = second_avg - first_avg
    
    if improvement > 5:
        return "improving"
    elif improvement < -5:
        return "declining"
    else:
        return "stable"

async def _generate_recommendations(db: AsyncSession, user_id: int, daily_data: List) -> List[str]:
    """Generate personalized recommendations for the user"""
    recommendations = []
    
    # Analyze study patterns
    study_times = [row[3] for row in daily_data]
    avg_study_time = sum(study_times) / len(study_times) if study_times else 0
    
    if avg_study_time < 15:  # Less than 15 minutes daily
        recommendations.append("Try to increase your daily study time to at least 15-20 minutes for better retention.")
    
    # Analyze accuracy patterns
    accuracies = [row[2] for row in daily_data]
    avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
    
    if avg_accuracy < 60:
        recommendations.append("Focus on understanding concepts before attempting more questions. Consider reviewing explanations.")
    elif avg_accuracy > 90:
        recommendations.append("Great accuracy! Try challenging yourself with harder difficulty questions.")
    
    # Analyze consistency
    active_days = len(daily_data)
    if active_days < 20:  # Less than 20 active days in last 30
        recommendations.append("Try to study more consistently. Daily practice, even for short periods, is more effective than sporadic long sessions.")
    
    return recommendations

# Export task functions
__all__ = [
    "aggregate_daily_analytics",
    "aggregate_weekly_analytics", 
    "update_question_analytics",
    "generate_weekly_reports",
    "calculate_user_insights"
]
