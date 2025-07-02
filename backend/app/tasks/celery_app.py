"""
Celery application configuration for background task processing.
Handles asynchronous tasks like AI processing, notifications, and analytics.
"""

import os
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "papa_backend",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.question_processing",
        "app.tasks.analytics_tasks", 
        "app.tasks.maintenance_tasks",
        "app.tasks.notification_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Task routing
    task_routes={
        "app.tasks.question_processing.*": {"queue": "question_processing"},
        "app.tasks.analytics_tasks.*": {"queue": "analytics"},
        "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
    },
    
    # Task priorities
    task_default_priority=5,
    worker_disable_rate_limits=False,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Daily analytics aggregation
    "aggregate-daily-analytics": {
        "task": "app.tasks.analytics_tasks.aggregate_daily_analytics",
        "schedule": crontab(hour=1, minute=0),  # Run at 1:00 AM daily
        "options": {"queue": "analytics", "priority": 3}
    },
    
    # Weekly analytics aggregation
    "aggregate-weekly-analytics": {
        "task": "app.tasks.analytics_tasks.aggregate_weekly_analytics", 
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday 2:00 AM
        "options": {"queue": "analytics", "priority": 3}
    },
    
    # Database cleanup
    "cleanup-old-sessions": {
        "task": "app.tasks.maintenance_tasks.cleanup_old_sessions",
        "schedule": crontab(hour=3, minute=0),  # Run at 3:00 AM daily
        "options": {"queue": "maintenance", "priority": 2}
    },
    
    # Clean up expired tokens
    "cleanup-expired-tokens": {
        "task": "app.tasks.maintenance_tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=3, minute=30),  # Run at 3:30 AM daily
        "options": {"queue": "maintenance", "priority": 2}
    },
    
    # Process pending questions
    "process-pending-questions": {
        "task": "app.tasks.question_processing.process_pending_questions_batch",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
        "options": {"queue": "question_processing", "priority": 6}
    },
    
    # Update question analytics
    "update-question-analytics": {
        "task": "app.tasks.analytics_tasks.update_question_analytics",
        "schedule": crontab(hour="*/2", minute=0),  # Every 2 hours
        "options": {"queue": "analytics", "priority": 4}
    },
    
    # Send daily summary notifications
    "send-daily-summaries": {
        "task": "app.tasks.notification_tasks.send_daily_summaries",
        "schedule": crontab(hour=8, minute=0),  # 8:00 AM daily
        "options": {"queue": "notifications", "priority": 7}
    },
    
    # Database backup (if enabled)
    "backup-database": {
        "task": "app.tasks.maintenance_tasks.backup_database",
        "schedule": crontab(hour=4, minute=0),  # 4:00 AM daily
        "options": {"queue": "maintenance", "priority": 1}
    },
    
    # Generate weekly reports
    "generate-weekly-reports": {
        "task": "app.tasks.analytics_tasks.generate_weekly_reports", 
        "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday 6:00 AM
        "options": {"queue": "analytics", "priority": 5}
    },
    
    # Health check for AI services
    "health-check-ai-services": {
        "task": "app.tasks.maintenance_tasks.health_check_ai_services",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"queue": "maintenance", "priority": 8}
    },
}

# Task soft time limits (in seconds)
celery_app.conf.task_soft_time_limit = 300  # 5 minutes
celery_app.conf.task_time_limit = 600  # 10 minutes hard limit

# Custom task base class
class BaseTask(celery_app.Task):
    """Base task class with common functionality"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        print(f"Task {task_id} failed: {exc}")
        # Log error to monitoring system
        # Send alert if critical task
        
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        print(f"Task {task_id} retrying due to: {exc}")
        
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        print(f"Task {task_id} completed successfully")

# Set custom base task
celery_app.Task = BaseTask

# Utility functions
def get_celery_worker_status():
    """Get status of all Celery workers"""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active = inspect.active()
        scheduled = inspect.scheduled()
        
        return {
            "workers": list(stats.keys()) if stats else [],
            "active_tasks": sum(len(tasks) for tasks in active.values()) if active else 0,
            "scheduled_tasks": sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0,
            "stats": stats
        }
    except Exception as e:
        return {"error": str(e)}

def purge_queue(queue_name: str):
    """Purge all tasks from a specific queue"""
    try:
        celery_app.control.purge()
        return {"status": "success", "queue": queue_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def revoke_task(task_id: str, terminate: bool = False):
    """Revoke a specific task"""
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Health check function
def celery_health_check():
    """Perform health check on Celery system"""
    try:
        # Test basic connectivity
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if not stats:
            return {"status": "unhealthy", "reason": "No workers available"}
            
        # Check if workers are responsive
        ping = inspect.ping()
        if not ping:
            return {"status": "unhealthy", "reason": "Workers not responding"}
            
        return {
            "status": "healthy",
            "workers": len(stats),
            "queues": ["question_processing", "analytics", "maintenance", "notifications"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Export the Celery app
__all__ = ["celery_app"]
