from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_logger, get_redis

logger = get_logger(__name__)

router = APIRouter()


@router.get("/state/{room_id}")
async def get_game_state(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Get game state for room {room_id} endpoint called")
    redis = get_redis()
    return {"message": f"Get game state for room {room_id} endpoint - to be implemented"}


@router.post("/action/{room_id}")
async def perform_action(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Perform action in room {room_id} endpoint called")
    redis = get_redis()
    return {"message": f"Perform action in room {room_id} endpoint - to be implemented"}


@router.post("/start/{room_id}")
async def start_game(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Start game in room {room_id} endpoint called")
    return {"message": f"Start game in room {room_id} endpoint - to be implemented"}


@router.post("/end/{room_id}")
async def end_game(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"End game in room {room_id} endpoint called")
    return {"message": f"End game in room {room_id} endpoint - to be implemented"}
