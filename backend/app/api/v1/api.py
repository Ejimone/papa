from fastapi import APIRouter

from app.api.v1.endpoints import auth, users
# Add other endpoint modules here as they are created
# from app.api.v1.endpoints import questions, practice, analytics, etc.

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
# api_router.include_router(practice.router, prefix="/practice", tags=["Practice"])
# api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
