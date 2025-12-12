from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_player
from app.core import get_db, get_logger
from app.models.player import Player
from app.schemas.room import RoomCreate, RoomDetail, RoomResponse, RoomUpdate
from app.services.room_service import RoomService

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=list[RoomResponse])
async def list_rooms(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List available rooms (not full, waiting for players)."""
    service = RoomService(db)
    try:
        rooms = await service.get_available_rooms(skip, limit)
        return rooms
    except Exception as e:
        logger.error(f"Error listing rooms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list rooms",
        )


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Create a new game room."""
    service = RoomService(db)
    try:
        room = await service.create_room(room_data, current_player.id)
        logger.info(
            f"Room created: {room.code}",
            extra={"room_code": room.code, "creator_id": current_player.id},
        )
        return room
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create room",
        )


@router.get("/{room_code}", response_model=RoomDetail)
async def get_room(
    room_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get room details by code."""
    service = RoomService(db)
    try:
        room = await service.get_room_by_code(room_code)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        room_with_members = await service.get_room_with_members(room.id)
        if not room_with_members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        members = [
            {
                "id": m.id,
                "player_id": m.player_id,
                "room_id": m.room_id,
                "is_ready": m.is_ready,
                "tank_color": m.tank_color,
                "joined_at": m.joined_at,
                "player_username": m.player.username if m.player else None,
            }
            for m in room_with_members.memberships
        ]

        return {
            **room.model_dump(),
            "members": members,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting room {room_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get room",
        )


@router.post("/{room_code}/join", response_model=RoomResponse)
async def join_room(
    room_code: str,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Join an existing room."""
    service = RoomService(db)
    try:
        room = await service.get_room_by_code(room_code)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        await service.join_room(room.id, current_player.id)
        logger.info(
            f"Player joined room: {room.code}",
            extra={"player_id": current_player.id, "room_code": room.code},
        )
        return room
    except ValueError as e:
        if "Room is full" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room is full",
            )
        elif "Player already in room" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player already in room",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
    except Exception as e:
        logger.error(f"Error joining room {room_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join room",
        )


@router.post("/{room_code}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(
    room_code: str,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Leave a room."""
    service = RoomService(db)
    try:
        room = await service.get_room_by_code(room_code)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        await service.leave_room(room.id, current_player.id)
        logger.info(
            f"Player left room: {room.code}",
            extra={"player_id": current_player.id, "room_code": room.code},
        )
        return None
    except Exception as e:
        logger.error(f"Error leaving room {room_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave room",
        )


@router.post("/{room_code}/ready/{is_ready}")
async def set_ready(
    room_code: str,
    is_ready: bool,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Set player ready status for a room."""
    service = RoomService(db)
    try:
        room = await service.get_room_by_code(room_code)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        await service.set_player_ready(room.id, current_player.id, is_ready)
        logger.info(
            f"Player ready status updated",
            extra={
                "player_id": current_player.id,
                "room_code": room.code,
                "is_ready": is_ready,
            },
        )
        return {"status": "ready" if is_ready else "not_ready"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error setting ready status in room {room_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set ready status",
        )


@router.post("/{room_code}/start", response_model=RoomResponse)
async def start_game(
    room_code: str,
    current_player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """Start a game (all players must be ready)."""
    service = RoomService(db)
    try:
        room = await service.get_room_by_code(room_code)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        room = await service.start_game(room.id)
        logger.info(
            f"Game started in room: {room.code}",
            extra={"initiated_by": current_player.id, "room_code": room.code},
        )
        return room
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error starting game in room {room_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start game",
        )
