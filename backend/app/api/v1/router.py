from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.skills import router as skills_router

api_v1_router = APIRouter()
api_v1_router.include_router(skills_router)
api_v1_router.include_router(admin_router)
