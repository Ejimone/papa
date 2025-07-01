from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_active_user

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_admin_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard data (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # In a real implementation, you would gather admin statistics
        return {
            "total_users": 0,
            "total_questions": 0,
            "total_subjects": 0,
            "active_sessions": 0,
            "system_status": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users", response_model=List[Dict[str, Any]])
async def get_all_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # In a real implementation, you would fetch and return user data
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
