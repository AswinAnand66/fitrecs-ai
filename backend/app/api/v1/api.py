from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.items import router as items_router
from app.api.recommend import router as recommend_router
from app.api.interactions import router as interactions_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(items_router, prefix="/items", tags=["items"])
api_router.include_router(recommend_router, prefix="/recommend", tags=["recommendations"])
api_router.include_router(interactions_router, prefix="/interactions", tags=["interactions"])