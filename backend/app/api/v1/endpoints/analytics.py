from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    UserAnalyticsRead, DashboardQuery, ReportQuery, AnalyticsExport,
    UserEventCreate, PerformanceTrendRead
)
from app.api.deps import get_current_active_user
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(
    days_back: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard data for the current user"""
    try:
        service = AnalyticsService(db)
        
        query = DashboardQuery(
            user_id=current_user.id,
            days_back=days_back
        )
        
        dashboard_data = await service.get_user_dashboard_data(current_user.id, query)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-analytics", response_model=UserAnalyticsRead)
async def get_user_analytics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for the current user"""
    try:
        service = AnalyticsService(db)
        analytics = await service.get_user_analytics(current_user.id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Analytics not found")
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events")
async def track_event(
    event_data: UserEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Track a user event"""
    try:
        service = AnalyticsService(db)
        event = await service.track_user_event(current_user.id, event_data)
        return {"message": "Event tracked successfully", "event_id": event.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-trends", response_model=List[PerformanceTrendRead])
async def get_performance_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance trends for the current user"""
    try:
        service = AnalyticsService(db)
        trends = await service.get_performance_trends(current_user.id, days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-activity", response_model=List[Dict[str, Any]])
async def get_weekly_activity(
    weeks_back: int = Query(4, ge=1, le=52, description="Number of weeks to look back"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get weekly activity data"""
    try:
        from app.models.analytics import DailyUserActivity
        from sqlalchemy import select, func
        from datetime import date
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        # Get daily activity data
        query = select(DailyUserActivity).where(
            DailyUserActivity.user_id == current_user.id,
            DailyUserActivity.date >= start_date,
            DailyUserActivity.date <= end_date
        ).order_by(DailyUserActivity.date)
        
        result = await db.execute(query)
        daily_activities = result.scalars().all()
        
        # Group by week
        weekly_data = {}
        for activity in daily_activities:
            week_start = activity.date - timedelta(days=activity.date.weekday())
            week_key = week_start.isoformat()
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    "week_start": week_key,
                    "questions_attempted": 0,
                    "correct_answers": 0,
                    "study_time_minutes": 0,
                    "sessions_completed": 0,
                    "days_active": 0
                }
            
            weekly_data[week_key]["questions_attempted"] += activity.questions_attempted
            weekly_data[week_key]["correct_answers"] += activity.correct_answers
            weekly_data[week_key]["study_time_minutes"] += activity.study_time_minutes
            weekly_data[week_key]["sessions_completed"] += activity.sessions_completed
            weekly_data[week_key]["days_active"] += 1
        
        # Calculate accuracy rates
        for week_data in weekly_data.values():
            attempted = week_data["questions_attempted"]
            correct = week_data["correct_answers"]
            week_data["accuracy_rate"] = (correct / attempted * 100) if attempted > 0 else 0
        
        return list(weekly_data.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subject-performance", response_model=List[Dict[str, Any]])
async def get_subject_performance(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance data by subject"""
    try:
        from app.models.analytics import SubjectPerformanceAnalytics
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        query = select(SubjectPerformanceAnalytics).options(
            selectinload(SubjectPerformanceAnalytics.subject)
        ).where(SubjectPerformanceAnalytics.user_id == current_user.id)
        
        result = await db.execute(query)
        performance_data = result.scalars().all()
        
        return [
            {
                "subject_id": perf.subject_id,
                "subject_name": perf.subject.name if perf.subject else "Unknown",
                "total_attempts": perf.total_attempts,
                "correct_attempts": perf.correct_attempts,
                "accuracy_rate": perf.accuracy_rate,
                "average_time_per_question": perf.average_time_per_question,
                "improvement_rate": perf.improvement_rate
            }
            for perf in performance_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-insights", response_model=Dict[str, Any])
async def get_learning_insights(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get learning insights and recommendations"""
    try:
        service = AnalyticsService(db)
        
        # Get recommendations
        recommendations = await service._get_recommendations(current_user.id)
        
        # Get performance level
        analytics = await service.get_user_analytics(current_user.id)
        performance_level = service._calculate_performance_level(analytics)
        
        # Get recent trends
        trends = await service._get_learning_trends(current_user.id, 14)  # Last 2 weeks
        
        return {
            "performance_level": performance_level,
            "recommendations": recommendations,
            "learning_trends": trends,
            "next_steps": [
                "Continue your daily practice streak",
                "Focus on improving weak areas",
                "Try more challenging questions",
                "Review previous mistakes"
            ][:3]  # Top 3 next steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/generate", response_model=Dict[str, Any])
async def generate_report(
    report_query: ReportQuery,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate an analytics report"""
    try:
        service = AnalyticsService(db)
        
        # Set user_id from current user if not provided or different
        if not hasattr(report_query, 'user_id') or report_query.user_id != current_user.id:
            report_query.user_id = current_user.id
        
        report = await service.generate_analytics_report(report_query)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export", response_model=Dict[str, Any])
async def export_analytics(
    export_type: str = Query(..., description="Type of export (csv, json, pdf)"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Export analytics data"""
    try:
        # Validate export type
        valid_types = ["csv", "json", "pdf"]
        if export_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid export type. Must be one of: {valid_types}")
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # In a real implementation, you would generate the actual export file
        # For now, return export information
        return {
            "export_type": export_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "user_id": current_user.id,
            "status": "generated",
            "download_url": f"/api/v1/analytics/download/{current_user.id}_{export_type}_{int(datetime.utcnow().timestamp())}",
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparison", response_model=Dict[str, Any])
async def get_performance_comparison(
    compare_with: str = Query("average", description="Compare with 'average' or 'top'"),
    period: str = Query("month", description="Comparison period: 'week', 'month', 'quarter'"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance comparison with other users"""
    try:
        from app.models.analytics import UserAnalytics
        from sqlalchemy import select, func
        
        # Get current user's analytics
        service = AnalyticsService(db)
        user_analytics = await service.get_user_analytics(current_user.id)
        
        if not user_analytics:
            raise HTTPException(status_code=404, detail="User analytics not found")
        
        # Get comparison data based on type
        if compare_with == "average":
            # Get average performance of all users
            avg_query = select(
                func.avg(UserAnalytics.overall_accuracy_rate).label('avg_accuracy'),
                func.avg(UserAnalytics.average_score).label('avg_score'),
                func.avg(UserAnalytics.total_study_time).label('avg_study_time')
            )
            
            avg_result = await db.execute(avg_query)
            avg_data = avg_result.first()
            
            comparison_data = {
                "accuracy_rate": avg_data.avg_accuracy or 0,
                "average_score": avg_data.avg_score or 0,
                "study_time": avg_data.avg_study_time or 0
            }
        
        elif compare_with == "top":
            # Get top 10% performance metrics
            top_query = select(
                func.percentile_cont(0.9).within_group(UserAnalytics.overall_accuracy_rate).label('top_accuracy'),
                func.percentile_cont(0.9).within_group(UserAnalytics.average_score).label('top_score'),
                func.percentile_cont(0.9).within_group(UserAnalytics.total_study_time).label('top_study_time')
            )
            
            top_result = await db.execute(top_query)
            top_data = top_result.first()
            
            comparison_data = {
                "accuracy_rate": top_data.top_accuracy or 0,
                "average_score": top_data.top_score or 0,
                "study_time": top_data.top_study_time or 0
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid comparison type")
        
        # Calculate differences
        user_accuracy = user_analytics.overall_accuracy_rate or 0
        user_score = user_analytics.average_score or 0
        user_study_time = user_analytics.total_study_time or 0
        
        return {
            "comparison_type": compare_with,
            "period": period,
            "your_performance": {
                "accuracy_rate": user_accuracy,
                "average_score": user_score,
                "study_time": user_study_time
            },
            "comparison_performance": comparison_data,
            "differences": {
                "accuracy_difference": user_accuracy - comparison_data["accuracy_rate"],
                "score_difference": user_score - comparison_data["average_score"],
                "study_time_difference": user_study_time - comparison_data["study_time"]
            },
            "percentile_rank": {
                "accuracy": 50,  # Would be calculated in real implementation
                "score": 50,
                "study_time": 50
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
