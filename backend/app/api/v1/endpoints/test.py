"""
Test endpoints for repository functionality.
These endpoints do not require authentication and are for development/testing only.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional

from app.schemas.user import UserRead
from app.core.database import get_db
from app.repositories.user_repository import user_repo
from app.models.user import User

router = APIRouter()

@router.get("/repository/user/methods")
async def test_user_repository_methods(
    db: AsyncSession = Depends(get_db)
):
    """
    Test various user repository methods without authentication.
    """
    results = {}
    
    try:
        # Test basic CRUD
        total_users = await user_repo.count(db)
        results["total_users"] = total_users
        
        # Test get by email (should be None for non-existent email)
        non_existent_user = await user_repo.get_by_email(db, email="nonexistent@test.com")
        results["non_existent_user_is_none"] = non_existent_user is None
        
        # Test active users in last 30 days
        active_users_30d = await user_repo.get_active_users(db, days=30, limit=5)
        results["active_users_last_30_days_count"] = len(active_users_30d)
        
        # Test leaderboard
        accuracy_leaderboard = await user_repo.get_leaderboard(db, metric="accuracy", days=30, limit=3)
        volume_leaderboard = await user_repo.get_leaderboard(db, metric="volume", days=30, limit=3)
        results["accuracy_leaderboard_entries"] = len(accuracy_leaderboard)
        results["volume_leaderboard_entries"] = len(volume_leaderboard)
        
        # Test search functionality
        search_results = await user_repo.search_users(db, query="test", limit=5)
        results["search_results_count"] = len(search_results)
        
        # Test users by university
        mit_users = await user_repo.get_users_by_university(db, university="MIT", limit=5)
        results["mit_users_count"] = len(mit_users)
        
        results["test_status"] = "success"
        results["repository_methods_tested"] = [
            "count", "get_by_email", "get_active_users", 
            "get_leaderboard", "search_users", "get_users_by_university"
        ]
        
    except Exception as e:
        results["test_status"] = "error"
        results["error_message"] = str(e)
        results["error_type"] = type(e).__name__
    
    return results


@router.get("/repository/user/leaderboard")
async def test_user_leaderboard(
    metric: str = Query("accuracy", regex="^(accuracy|volume)$", description="Leaderboard metric"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=100, description="Number of top users to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Test user leaderboard functionality without authentication.
    """
    try:
        leaderboard = await user_repo.get_leaderboard(db, metric=metric, days=days, limit=limit)
        return {
            "status": "success",
            "metric": metric,
            "days": days,
            "limit": limit,
            "results_count": len(leaderboard),
            "leaderboard": leaderboard
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }


@router.get("/repository/user/search")
async def test_user_search(
    query: str = Query(..., description="Search term for username or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Test user search functionality without authentication.
    """
    try:
        users = await user_repo.search_users(db, query=query, skip=skip, limit=limit)
        return {
            "status": "success",
            "query": query,
            "skip": skip,
            "limit": limit,
            "results_count": len(users),
            "users": [{"id": u.id, "username": u.username, "email": u.email} for u in users]
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }


@router.get("/repository/user/active")
async def test_active_users(
    days: int = Query(7, ge=1, le=365, description="Number of days to look back for activity"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Test active users functionality without authentication.
    """
    try:
        users = await user_repo.get_active_users(db, days=days, skip=skip, limit=limit)
        return {
            "status": "success",
            "days": days,
            "skip": skip,
            "limit": limit,
            "results_count": len(users),
            "users": [{"id": u.id, "username": u.username, "last_login_at": u.last_login_at} for u in users]
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }


@router.get("/repository/user/by-university")
async def test_users_by_university(
    university: str = Query(..., description="University name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Test users by university functionality without authentication.
    """
    try:
        users = await user_repo.get_users_by_university(db, university=university, skip=skip, limit=limit)
        return {
            "status": "success",
            "university": university,
            "skip": skip,
            "limit": limit,
            "results_count": len(users),
            "users": [{"id": u.id, "username": u.username, "email": u.email} for u in users]
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }


@router.get("/database/status")
async def test_database_connection(
    db: AsyncSession = Depends(get_db)
):
    """
    Test basic database connectivity and table existence.
    """
    try:
        # Test basic query
        result = await db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        
        # Test if users table exists
        table_check = await db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """))
        users_table_exists = table_check.scalar()
        
        # Count users if table exists
        user_count = None
        if users_table_exists:
            count_result = await db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = count_result.scalar()
        
        return {
            "status": "success",
            "database_connection": test_value == 1,
            "users_table_exists": users_table_exists,
            "user_count": user_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }


@router.get("/repository/user/create-sample")
async def create_sample_user(
    db: AsyncSession = Depends(get_db)
):
    """
    Create a sample user for testing (only if no users exist).
    """
    try:
        # Check if any users exist
        user_count = await user_repo.count(db)
        
        if user_count > 0:
            return {
                "status": "skipped",
                "message": f"Users already exist ({user_count} users found). No sample user created.",
                "user_count": user_count
            }
        
        # Create a sample user
        from app.schemas.user import UserCreate
        from app.core.security import get_password_hash
        
        sample_user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        
        # Hash the password
        hashed_password = get_password_hash(sample_user_data.password)
        
        # Create user object
        user_dict = sample_user_data.dict()
        user_dict.pop('password')  # Remove plain password
        user_dict['hashed_password'] = hashed_password
        
        # Create the user
        new_user = await user_repo.create(db, obj_in=user_dict)
        
        return {
            "status": "success",
            "message": "Sample user created successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "is_active": new_user.is_active
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }
