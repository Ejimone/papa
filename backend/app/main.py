from fastapi import FastAPI
from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
# from app.core.events import create_start_app_handler, create_stop_app_handler # Will be added later

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# app.add_event_handler("startup", create_start_app_handler(app)) # Will be added later
# app.add_event_handler("shutdown", create_stop_app_handler(app)) # Will be added later

app.include_router(api_router_v1, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
