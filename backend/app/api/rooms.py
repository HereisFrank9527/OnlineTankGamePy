from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("")
async def list_rooms(db: AsyncSession = Depends(get_db)):
    logger.info("List rooms endpoint called")
    return {"message": "List rooms endpoint - to be implemented"}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_room(db: AsyncSession = Depends(get_db)):
    logger.info("Create room endpoint called")
    return {"message": "Create room endpoint - to be implemented"}


@router.get("/{room_id}")
async def get_room(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Get room {room_id} endpoint called")
    return {"message": f"Get room {room_id} endpoint - to be implemented"}


@router.put("/{room_id}")
async def update_room(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Update room {room_id} endpoint called")
    return {"message": f"Update room {room_id} endpoint - to be implemented"}


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Delete room {room_id} endpoint called")
    return


@router.post("/{room_id}/join")
async def join_room(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Join room {room_id} endpoint called")
    return {"message": f"Join room {room_id} endpoint - to be implemented"}


@router.post("/{room_id}/leave")
async def leave_room(room_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Leave room {room_id} endpoint called")
    return {"message": f"Leave room {room_id} endpoint - to be implemented"}
