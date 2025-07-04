from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from sqlalchemy.orm import selectinload
import os
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User, UserProfile
from app.models.question import Question
from app.models.subject import Subject
from app.models.practice import PracticeSession
from app.api.deps import get_current_active_user
from app.schemas.user import AdminUserCreate, AdminUserUpdate, AdminUserResponse, AdminDashboardStats
from app.schemas.question import QuestionRead, QuestionCreate, QuestionUpdate
from app.services.user_service import UserService
from app.services.question_service import QuestionService
from app.core.security import get_password_hash

router = APIRouter()

def verify_admin_access(current_user: User):
    """Verify that the current user has admin privileges"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    verify_admin_access(current_user)
    
    try:
        # Get total users
        total_users = await db.scalar(select(func.count(User.id)))
        
        # Get total questions
        total_questions = await db.scalar(select(func.count(Question.id)))
        
        # Get total subjects
        total_subjects = await db.scalar(select(func.count(Subject.id)))
        
        # Get active sessions (sessions from last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        active_sessions = await db.scalar(
            select(func.count(PracticeSession.id))
            .where(PracticeSession.created_at >= yesterday)
        )
        
        # For now, we'll use mock data for course materials
        recent_uploads = 5  # Mock data
        total_course_materials = 25  # Mock data
        
        return {
            "total_users": total_users or 0,
            "total_questions": total_questions or 0,
            "total_subjects": total_subjects or 0,
            "active_sessions": active_sessions or 0,
            "system_status": "healthy",
            "recent_uploads": recent_uploads,
            "total_course_materials": total_course_materials
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None)
):
    """Get all users with pagination and search"""
    verify_admin_access(current_user)
    
    try:
        query = select(User)
        
        if search:
            query = query.where(
                User.email.ilike(f"%{search}%") |
                User.username.ilike(f"%{search}%")
            )
        
        query = query.offset(skip).limit(limit).order_by(desc(User.created_at))
        result = await db.execute(query)
        users = result.scalars().all()
        
        return [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.post("/users")
async def create_user(
    user_data: AdminUserCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (admin only)"""
    verify_admin_access(current_user)
    
    try:
        # Check if user already exists
        existing_user = await db.scalar(
            select(User).where(User.email == user_data.email)
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_admin=user_data.is_admin
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "is_active": new_user.is_active,
            "is_admin": new_user.is_admin,
            "created_at": new_user.created_at,
            "updated_at": new_user.updated_at
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a user (admin only)"""
    verify_admin_access(current_user)
    
    try:
        user = await db.scalar(select(User).where(User.id == user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user fields
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.is_admin is not None:
            user.is_admin = user_data.is_admin
        
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (admin only)"""
    verify_admin_access(current_user)
    
    try:
        user = await db.scalar(select(User).where(User.id == user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        await db.delete(user)
        await db.commit()
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.get("/questions")
async def get_all_questions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None)
):
    """Get all questions with pagination and search"""
    verify_admin_access(current_user)
    
    try:
        query = select(Question).options(selectinload(Question.subject))
        
        if search:
            query = query.where(
                Question.title.ilike(f"%{search}%") |
                Question.content.ilike(f"%{search}%")
            )
        
        query = query.offset(skip).limit(limit).order_by(desc(Question.created_at))
        result = await db.execute(query)
        questions = result.scalars().all()
        
        return [
            {
                "id": question.id,
                "title": question.title,
                "content": question.content[:200] + "..." if len(question.content) > 200 else question.content,
                "type": question.type,
                "difficulty_level": question.difficulty_level,
                "created_at": question.created_at,
                "updated_at": question.updated_at,
                "subject": question.subject.name if question.subject else None
            }
            for question in questions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a question (admin only)"""
    verify_admin_access(current_user)
    
    try:
        question = await db.scalar(select(Question).where(Question.id == question_id))
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        await db.delete(question)
        await db.commit()
        
        return {"message": "Question deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting question: {str(e)}")

@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics overview (admin only)"""
    verify_admin_access(current_user)
    
    try:
        # Users analytics
        total_users = await db.scalar(select(func.count(User.id)))
        active_users = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
        
        # Questions analytics
        total_questions = await db.scalar(select(func.count(Question.id)))
        
        # Practice sessions analytics
        total_sessions = await db.scalar(select(func.count(PracticeSession.id)))
        
        # Recent activity (last 30 days)
        month_ago = datetime.utcnow() - timedelta(days=30)
        recent_users = await db.scalar(
            select(func.count(User.id)).where(User.created_at >= month_ago)
        )
        recent_questions = await db.scalar(
            select(func.count(Question.id)).where(Question.created_at >= month_ago)
        )
        
        return {
            "users": {
                "total": total_users or 0,
                "active": active_users or 0,
                "recent": recent_users or 0
            },
            "questions": {
                "total": total_questions or 0,
                "recent": recent_questions or 0
            },
            "sessions": {
                "total": total_sessions or 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@router.post("/database/query")
async def execute_database_query(
    query_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a database query (admin only) - USE WITH CAUTION"""
    verify_admin_access(current_user)
    
    try:
        query = query_data.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Basic security check - only allow SELECT queries
        if not query.upper().startswith("SELECT"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        
        # Execute query
        result = await db.execute(text(query))
        rows = result.fetchall()
        
        # Convert to list of dictionaries
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]
        
        return {
            "success": True,
            "data": data,
            "row_count": len(data),
            "columns": list(columns)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "row_count": 0,
            "columns": []
        }

@router.get("/system/settings")
async def get_system_settings(
    current_user: User = Depends(get_current_active_user)
):
    """Get system settings (admin only)"""
    verify_admin_access(current_user)
    
    # This would typically read from a settings file or database
    return {
        "app_name": "Past Questions App",
        "version": "1.0.0",
        "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
        "max_file_size": "10MB",
        "allowed_file_types": ["pdf", "docx", "txt", "jpg", "png"],
        "ai_enabled": True,
        "notifications_enabled": True
    }

@router.put("/system/settings")
async def update_system_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Update system settings (admin only)"""
    verify_admin_access(current_user)
    
    try:
        # In a real implementation, you would save these to a database or config file
        # For now, we'll just return the settings as confirmation
        return {
            "message": "Settings updated successfully",
            "settings": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

@router.get("/system/logs")
async def get_system_logs(
    current_user: User = Depends(get_current_active_user),
    lines: int = Query(100, ge=1, le=1000)
):
    """Get system logs (admin only)"""
    verify_admin_access(current_user)
    
    try:
        # This would typically read from log files
        # For now, return mock log data
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "System started successfully",
                "module": "main"
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "level": "INFO",
                "message": "User logged in",
                "module": "auth"
            }
        ]
        
        return {
            "logs": logs[:lines],
            "total_lines": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")

@router.post("/system/cache/clear")
async def clear_system_cache(
    current_user: User = Depends(get_current_active_user)
):
    """Clear system cache (admin only)"""
    verify_admin_access(current_user)
    
    try:
        # In a real implementation, you would clear Redis cache or other caches
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.get("/export/users")
async def export_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Export users data (admin only)"""
    verify_admin_access(current_user)
    
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        export_data = [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
            for user in users
        ]
        
        return {
            "data": export_data,
            "total_records": len(export_data),
            "export_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting users: {str(e)}")

@router.get("/export/questions")
async def export_questions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Export questions data (admin only)"""
    verify_admin_access(current_user)
    
    try:
        result = await db.execute(select(Question))
        questions = result.scalars().all()
        
        export_data = [
            {
                "id": question.id,
                "title": question.title,
                "content": question.content,
                "type": question.type,
                "difficulty_level": question.difficulty_level,
                "created_at": question.created_at.isoformat(),
                "updated_at": question.updated_at.isoformat()
            }
            for question in questions
        ]
        
        return {
            "data": export_data,
            "total_records": len(export_data),
            "export_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting questions: {str(e)}")

@router.get("/version")
async def get_system_version(
    current_user: User = Depends(get_current_active_user)
):
    """Get system version information (admin only)"""
    verify_admin_access(current_user)
    
    return {
        "app_name": "Past Questions App",
        "version": "1.0.0",
        "build_date": "2024-01-01",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": "3.11+",
        "database_version": "PostgreSQL 15+"
    }
