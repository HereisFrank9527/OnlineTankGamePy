"""
WebSocket endpoint for real-time game synchronization.

Connection flow:
1. Client connects to /ws/game/{room_code}?token={jwt_token}
2. Server validates JWT and loads player/room data
3. Client sends/receives JSON messages
4. Server broadcasts to all room participants
5. Client disconnection triggers cleanup
"""

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocketException, status
from fastapi.websockets import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import decode_token, get_db, get_logger, get_redis
from app.models.player import Player
from app.models.room import Room, RoomStatus
from app.repositories.player import PlayerRepository
from app.repositories.room import RoomRepository
from app.repositories.tank_state import TankStateRepository
from app.schemas.ws import (
    FireData,
    MessageType,
    PlayerJoinData,
    PlayerLeaveData,
    ScoreboardData,
    ScoreboardEntry,
    TankStateUpdateData,
    WSMessage,
)
from app.ws.manager import WSConnectionManager

logger = get_logger(__name__)

router = APIRouter()

ws_managers: dict[str, WSConnectionManager] = {}


def get_ws_manager(room_code: str) -> WSConnectionManager:
    """Get or create WebSocket manager for a room."""
    if room_code not in ws_managers:
        redis = get_redis()
        ws_managers[room_code] = WSConnectionManager(redis)
    return ws_managers[room_code]


async def authenticate_ws_token(token: str | None = Query(None)) -> int:
    """
    Authenticate WebSocket connection via JWT token query parameter.
    
    Args:
        token: JWT access token
    
    Returns:
        Player ID
    
    Raises:
        WebSocketException: If token is invalid or missing
    """
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token required")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")

    subject = payload.get("sub")
    try:
        return int(subject)
    except (TypeError, ValueError):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token subject"
        )


@router.websocket("/ws/game/{room_code}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_code: str,
    player_id: int = Depends(authenticate_ws_token),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time game synchronization.
    
    Query Parameters:
        token: JWT access token (required)
    
    Path Parameters:
        room_code: Game room code
    """
    player_repo = PlayerRepository(db)
    room_repo = RoomRepository(db)
    tank_repo = TankStateRepository(db)
    manager = get_ws_manager(room_code)

    try:
        player = await player_repo.get(player_id)
        if not player:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Player not found"
            )
            return

        room = await room_repo.get_by_code(room_code)
        if not room:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Room not found"
            )
            return

        if room.status == RoomStatus.FINISHED:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Room is finished"
            )
            return

        await manager.connect(websocket, room_code, player_id)

        join_msg = WSMessage(
            type=MessageType.JOIN,
            data=PlayerJoinData(
                player_id=player_id,
                username=player.username,
                tank_color=None,
            ).model_dump(),
        )
        await manager.broadcast(room_code, join_msg, exclude_websocket=websocket)

        await websocket.send_text(
            WSMessage(
                type=MessageType.JOIN,
                data={"player_id": player_id, "username": player.username},
            ).model_dump_json()
        )

        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")

                if message_type == MessageType.TANK_STATE_UPDATE:
                    tank_data = TankStateUpdateData(**message_data.get("data", {}))

                    if tank_data.player_id != player_id:
                        await manager.send_error(
                            websocket, "INVALID_PLAYER", "Cannot update other player state"
                        )
                        continue

                    tank_state = await tank_repo.get_by_player_and_room(player_id, room.id)
                    if tank_state:
                        tank_state.position_x = tank_data.position_x
                        tank_state.position_y = tank_data.position_y
                        tank_state.rotation = tank_data.rotation
                        tank_state.velocity_x = tank_data.velocity_x
                        tank_state.velocity_y = tank_data.velocity_y
                        tank_state.hp = tank_data.hp
                        await tank_repo.update(tank_state)

                    await manager.broadcast(
                        room_code,
                        WSMessage(type=MessageType.TANK_STATE_UPDATE, data=tank_data.model_dump()),
                    )

                elif message_type == MessageType.FIRE:
                    fire_data = FireData(**message_data.get("data", {}))

                    if fire_data.player_id != player_id:
                        await manager.send_error(
                            websocket, "INVALID_PLAYER", "Cannot fire from other player"
                        )
                        continue

                    await manager.broadcast(
                        room_code, WSMessage(type=MessageType.FIRE, data=fire_data.model_dump())
                    )

                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_error(
                    websocket, "INVALID_MESSAGE", "Message format is invalid"
                )

    except Exception as e:
        logger.error(f"WebSocket error: {e}", extra={"player_id": player_id, "room_code": room_code})
        manager.disconnect(websocket, room_code)
        if not websocket.client_state.disconnected:
            try:
                await websocket.close()
            except Exception:
                pass
    finally:
        if websocket in manager.connection_player_map:
            manager.disconnect(websocket, room_code)
            leave_msg = WSMessage(
                type=MessageType.LEAVE,
                data=PlayerLeaveData(
                    player_id=player_id,
                    username=player.username,
                ).model_dump(),
            )
            try:
                await manager.broadcast(room_code, leave_msg)
            except Exception as e:
                logger.error(f"Error broadcasting leave message: {e}")


@router.get("/ws/scoreboard/{room_code}")
async def get_room_scoreboard(
    room_code: str, db: AsyncSession = Depends(get_db)
):
    """
    Get current room scoreboard derived from player stats and tank state.
    
    Returns leaderboard entries sorted by kills.
    """
    room_repo = RoomRepository(db)
    tank_repo = TankStateRepository(db)

    room = await room_repo.get_by_code(room_code)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )

    room_with_members = await room_repo.get_with_members(room.id)
    if not room_with_members:
        return {"entries": []}

    entries = []
    for membership in room_with_members.memberships:
        player = membership.player
        tank_state = await tank_repo.get_by_player_and_room(player.id, room.id)

        entry = ScoreboardEntry(
            player_id=player.id,
            username=player.username,
            kills=player.kills,
            deaths=player.deaths,
            hp=tank_state.hp if tank_state else 0,
        )
        entries.append(entry)

    entries.sort(key=lambda e: e.kills, reverse=True)

    return ScoreboardData(entries=entries)
