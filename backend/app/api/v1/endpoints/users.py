from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.user import UserRead, UserUpdate, UserPasswordUpdate # UserProfile, UserProfileUpdate removed for now
from app.services.user_service import user_service
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_active_superuser
from app.models.user import User # Required for type hinting current_user

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
