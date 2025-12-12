from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(db: AsyncSession = Depends(get_db)):
    logger.info("Register endpoint called")
    return {"message": "Registration endpoint - to be implemented"}


@router.post("/login")
async def login(db: AsyncSession = Depends(get_db)):
    logger.info("Login endpoint called")
    return {"message": "Login endpoint - to be implemented"}


@router.post("/refresh")
async def refresh_token():
    logger.info("Refresh token endpoint called")
    return {"message": "Refresh token endpoint - to be implemented"}


@router.post("/logout")
async def logout():
    logger.info("Logout endpoint called")
    return {"message": "Logout endpoint - to be implemented"}


@router.get("/me")
async def get_current_user(db: AsyncSession = Depends(get_db)):
    logger.info("Get current user endpoint called")
    return {"message": "Get current user endpoint - to be implemented"}
