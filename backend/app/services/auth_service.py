from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, Token
from app.models.user import User
from app.repositories.user_repository import user_repo
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.config import settings

class AuthService:
    async def register_user(self, db: AsyncSession, *, user_in: UserCreate) -> User:
        existing_user_email = await user_repo.get_by_email(db, email=user_in.email)
        if existing_user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists.",
            )
        if user_in.username:
            existing_user_username = await user_repo.get_by_username(db, username=user_in.username)
            if existing_user_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this username already exists.",
                )

        hashed_password = get_password_hash(user_in.password)

        user_data_for_db = user_in.model_dump(exclude={"password"})
        user_data_for_db["hashed_password"] = hashed_password

        # Check if this is the first user and make them superuser
        # This is a simple way; a more robust way might be a CLI command or checking count in DB
        if user_in.email == settings.FIRST_SUPERUSER_EMAIL:
             user_data_for_db["is_superuser"] = True

        # We need to create a User model instance from the dict for the repository
        # The repository's create method expects a Pydantic schema, but we've modified the data
        # Let's adjust to pass the dict directly if the repository supports it, or create a temp schema.
        # For now, let's assume the repository can handle a dict, or we'll adjust the base repo.
        # A better way for BaseRepository.create would be to accept a dictionary.
        # Let's modify the base repository to accept a dictionary for creation.
        # For now, creating a User object directly:

        db_user = User(**user_data_for_db)
        db.add(db_user)
        await db.flush()
        await db.refresh(db_user)
        return db_user


    async def login_user(self, db: AsyncSession, *, login_data: LoginRequest) -> Token:
        user = await user_repo.get_by_email(db, email=login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not await user_repo.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user.",
            )

        access_token = create_access_token(subject=user.id) # Use user.id or user.email as subject
        refresh_token = create_refresh_token(subject=user.id)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, db: AsyncSession, *, refresh_token_value: str) -> Token:
        # This is a simplified refresh token logic.
        # In a real app, you'd store and validate refresh tokens more securely (e.g., in DB, check revocation)
        payload = decode_token(refresh_token_value)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await user_repo.get(db, id=int(user_id))
        if not user or not await user_repo.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_access_token = create_access_token(subject=user.id)
        # Optionally, issue a new refresh token (e.g., for refresh token rotation)
        # new_refresh_token = create_refresh_token(subject=user.id)
        return Token(access_token=new_access_token, refresh_token=refresh_token_value) # or new_refresh_token


auth_service = AuthService()
