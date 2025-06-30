from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        return await self.get_by_attribute(db, attribute="email", value=email)

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        return await self.get_by_attribute(db, attribute="username", value=username)

    async def is_active(self, user: User) -> bool:
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        return user.is_superuser

# Initialize repository instance for use in services/endpoints
user_repo = UserRepository(User)
