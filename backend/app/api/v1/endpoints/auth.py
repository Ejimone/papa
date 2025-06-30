from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, Token, RefreshTokenRequest
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import auth_service
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User # Required for type hinting get_current_active_user

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new user.
    """
    user = await auth_service.register_user(db=db, user_in=user_in)
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest, # Can use OAuth2PasswordRequestForm = Depends() for form data
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    token = await auth_service.login_user(db=db, login_data=login_data)
    return token

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token.
    """
    token = await auth_service.refresh_access_token(db=db, refresh_token_value=refresh_request.refresh_token)
    return token

@router.post("/logout") # Invalidate token on client-side, or implement server-side blacklist
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout user (client-side token removal or server-side token invalidation).
    For true stateless JWT, logout is handled by the client deleting the token.
    If server-side invalidation is needed, a token blacklist (e.g., in Redis) is required.
    """
    # This is a placeholder. Actual logout for JWT is client-side.
    # If you implement a token blacklist, you'd add the token to it here.
    return {"msg": "Successfully logged out. Please delete your token."}

# Password recovery/reset endpoints would go here later
# @router.post("/forgot-password")
# async def forgot_password(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
#     # ... logic to send password reset email ...
#     return {"msg": "Password reset email sent if user exists."}

# @router.post("/reset-password")
# async def reset_password(request: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
#     # ... logic to validate token and reset password ...
#     return {"msg": "Password has been reset."}
