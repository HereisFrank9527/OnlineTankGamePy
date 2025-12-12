from fastapi import APIRouter

from app.api import auth, gameplay, rooms

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(gameplay.router, prefix="/gameplay", tags=["gameplay"])

__all__ = ["api_router"]
