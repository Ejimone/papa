from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from app.schemas.user import UserRead, UserUpdate, UserPasswordUpdate # UserProfile, UserProfileUpdate removed for now
from app.services.user_service import user_service
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_active_superuser
from app.models.user import User # Required for type hinting current_user
from app.repositories.user_repository import user_repo

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserRead)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate, # For now, UserUpdate can handle basic profile fields like email/username
    current_user: User = Depends(get_current_active_user)
):
    """
    Update own user.
    """
    user = await user_service.update_user_profile(db=db, current_user=current_user, user_in=user_in)
    return user

@router.put("/me/password", response_model=UserRead) # Or a simple success message
async def update_password_me(
    *,
    db: AsyncSession = Depends(get_db),
    password_in: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update own password.
    """
    user = await user_service.update_user_password(db=db, current_user=current_user, password_in=password_in)
    return user


# Example Admin routes (can be expanded or moved to admin.py)
@router.get("/", response_model=List[UserRead], dependencies=[Depends(get_current_active_superuser)])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: User = Depends(get_current_active_superuser) # Dependency already in decorator
):
    """
    Retrieve users (Superuser only).
    """
    # This directly uses the repo, could also be a service method
    from app.repositories.user_repository import user_repo
    users = await user_repo.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_active_superuser)])
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_active_superuser) # Dependency already in decorator
):
    """
    Get a specific user by id (Superuser only).
    """
    user = await user_service.get_user_by_id(db, user_id=user_id)
    return user


@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_active_superuser)])
async def update_user_by_id(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    user_in: UserUpdate, # Admin can update more fields
    # current_user: User = Depends(get_current_active_superuser) # Dependency already in decorator
):
    """
    Update a user (Superuser only).
    """
    user_to_update = await user_service.get_user_by_id(db, user_id=user_id) # Fetch user first
    # Superusers can change is_active and is_superuser status
    # The user_in schema (UserUpdate) might need to be different for admin (e.g. UserUpdateAdmin)
    # For now, UserUpdate is used, but the service layer should handle permissions for setting is_superuser.
    # The user_service.update_user_profile currently prevents non-superusers from escalating privileges.
    # A superuser making this call would have current_user.is_superuser = True, so the service method needs
    # to account for that if it's going to be reused for admin updates.
    # Or, create a separate admin_update_user service method.

    # Simplified: Assume user_service.update_user_profile can handle admin updates if current_user is superuser
    # This might need refinement in the service layer.
    updated_user = await user_service.update_user_profile(db=db, current_user=user_to_update, user_in=user_in)
    return updated_user


# Repository Testing Endpoints

@router.get("/me/statistics", response_model=Dict[str, Any])
async def get_my_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive statistics for the current user.
    """
    stats = await user_repo.get_user_statistics(db, user_id=current_user.id)
    return stats


@router.get("/me/profile", response_model=UserRead)
async def get_my_profile_with_details(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user with profile and preferences loaded.
    """
    user_with_profile = await user_repo.get_with_profile(db, user_id=current_user.id)
    if not user_with_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return user_with_profile


@router.post("/me/update-last-login")
async def update_my_last_login(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the last login timestamp for the current user.
    """
    updated_user = await user_repo.update_last_login(db, user_id=current_user.id)
    return {"message": "Last login updated", "last_login_at": updated_user.last_login_at}


@router.get("/search", response_model=List[UserRead], dependencies=[Depends(get_current_active_superuser)])
async def search_users(
    query: str = Query(..., description="Search term for username or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Search users by username or email (Superuser only).
    """
    users = await user_repo.search_users(db, query=query, skip=skip, limit=limit)
    return users


@router.get("/active", response_model=List[UserRead], dependencies=[Depends(get_current_active_superuser)])
async def get_active_users(
    days: int = Query(7, ge=1, le=365, description="Number of days to look back for activity"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get users who have been active in the last N days (Superuser only).
    """
    users = await user_repo.get_active_users(db, days=days, skip=skip, limit=limit)
    return users


@router.get("/by-university", response_model=List[UserRead], dependencies=[Depends(get_current_active_superuser)])
async def get_users_by_university(
    university: str = Query(..., description="University name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get users from a specific university (Superuser only).
    """
    users = await user_repo.get_users_by_university(db, university=university, skip=skip, limit=limit)
    return users


@router.get("/leaderboard", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    metric: str = Query("accuracy", pattern="^(accuracy|volume)$", description="Leaderboard metric"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=100, description="Number of top users to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user leaderboard based on different metrics.
    """
    leaderboard = await user_repo.get_leaderboard(db, metric=metric, days=days, limit=limit)
    return leaderboard


@router.get("/statistics/{user_id}", response_model=Dict[str, Any], dependencies=[Depends(get_current_active_superuser)])
async def get_user_statistics_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive statistics for a specific user (Superuser only).
    """
    # First check if user exists
    user = await user_repo.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = await user_repo.get_user_statistics(db, user_id=user_id)
    return stats


@router.post("/{user_id}/deactivate", dependencies=[Depends(get_current_active_superuser)])
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a user account (Superuser only).
    """
    user = await user_repo.deactivate_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user.username} has been deactivated", "is_active": user.is_active}


@router.post("/{user_id}/reactivate", dependencies=[Depends(get_current_active_superuser)])
async def reactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivate a user account (Superuser only).
    """
    user = await user_repo.reactivate_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user.username} has been reactivated", "is_active": user.is_active}


# Advanced Repository Testing Endpoints

@router.get("/test/repository-methods", dependencies=[Depends(get_current_active_superuser)])
async def test_repository_methods(
    db: AsyncSession = Depends(get_db)
):
    """
    Test various repository methods (Superuser only - for development/testing).
    """
    results = {}
    
    try:
        # Test basic CRUD
        total_users = await user_repo.count(db)
        results["total_users"] = total_users
        
        # Test get by email (should be None for non-existent email)
        non_existent_user = await user_repo.get_by_email(db, email="nonexistent@test.com")
        results["non_existent_user"] = non_existent_user is None
        
        # Test active users in last 30 days
        active_users_30d = await user_repo.get_active_users(db, days=30, limit=5)
        results["active_users_last_30_days"] = len(active_users_30d)
        
        # Test leaderboard
        accuracy_leaderboard = await user_repo.get_leaderboard(db, metric="accuracy", days=30, limit=3)
        volume_leaderboard = await user_repo.get_leaderboard(db, metric="volume", days=30, limit=3)
        results["accuracy_leaderboard_entries"] = len(accuracy_leaderboard)
        results["volume_leaderboard_entries"] = len(volume_leaderboard)
        
        # Test search functionality
        search_results = await user_repo.search_users(db, query="test", limit=5)
        results["search_results_count"] = len(search_results)
        
        results["test_status"] = "success"
        
    except Exception as e:
        results["test_status"] = "error"
        results["error_message"] = str(e)
    
    return results
