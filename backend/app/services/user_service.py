from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User
from app.schemas.user import UserUpdate, UserPasswordUpdate
from app.repositories.user_repository import user_repo
from app.core.security import get_password_hash, verify_password

class UserService:
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        user = await user_repo.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def update_user_profile(self, db: AsyncSession, *, current_user: User, user_in: UserUpdate) -> User:
        # Ensure email uniqueness if it's being changed
        if user_in.email and user_in.email != current_user.email:
            existing_user = await user_repo.get_by_email(db, email=user_in.email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered by another user.",
                )

        # Ensure username uniqueness if it's being changed
        if user_in.username and user_in.username != current_user.username:
            existing_user = await user_repo.get_by_username(db, username=user_in.username)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken.",
                )

        # Prevent non-superusers from making themselves superuser or changing active status directly
        # Superusers can only be set by other superusers or system processes
        update_data = user_in.model_dump(exclude_unset=True)
        if not current_user.is_superuser:
            if "is_superuser" in update_data:
                del update_data["is_superuser"]
            # if "is_active" in update_data: # Regular users usually shouldn't deactivate themselves this way
            #     del update_data["is_active"]


        updated_user = await user_repo.update(db, db_obj=current_user, obj_in=update_data)
        return updated_user

    async def update_user_password(self, db: AsyncSession, *, current_user: User, password_in: UserPasswordUpdate) -> User:
        if not verify_password(password_in.current_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

        new_hashed_password = get_password_hash(password_in.new_password)
        updated_user = await user_repo.update(db, db_obj=current_user, obj_in={"hashed_password": new_hashed_password})
        return updated_user

user_service = UserService()
