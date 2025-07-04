from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, ai, subjects, questions, practice, analytics, search, admin, upload, notifications, course_materials
# Add other endpoint modules here as they are created
# from app.api.v1.endpoints import questions, practice, analytics, etc.

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(practice.router, prefix="/practice", tags=["practice"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(course_materials.router, prefix="/course-materials", tags=["course-materials"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
# api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
# api_router.include_router(practice.router, prefix="/practice", tags=["Practice"])
# api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
