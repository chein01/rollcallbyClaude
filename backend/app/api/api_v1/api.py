from fastapi import APIRouter

from app.api.api_v1.endpoints import users, checkins

api_router = APIRouter()

# Include specific API endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["checkins"])