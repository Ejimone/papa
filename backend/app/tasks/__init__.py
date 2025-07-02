"""
Tasks module for background processing.

This module contains all background task definitions for:
- Question processing (AI embedding, OCR, explanations)
- Analytics aggregation and reporting
- System maintenance and cleanup
- User notifications and communications

Usage:
    from app.tasks import celery_app
    from app.tasks.question_processing import process_question_embeddings
    from app.tasks.analytics_tasks import aggregate_daily_analytics
"""

from app.tasks.celery_app import celery_app

# Import task modules to register them with Celery
from app.tasks import question_processing
from app.tasks import analytics_tasks
from app.tasks import maintenance_tasks
from app.tasks import notification_tasks

__all__ = [
    "celery_app",
    "question_processing",
    "analytics_tasks", 
    "maintenance_tasks",
    "notification_tasks"
]
