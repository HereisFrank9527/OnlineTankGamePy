"""
WebSocket connection manager with Redis pub/sub integration for horizontal scaling.

Tracks active connections per room, broadcasts messages to participants,
and uses Redis pub/sub to sync messages across multiple server instances.
"""

import json
from typing import Callable

from fastapi import WebSocketException
from fastapi.websockets import WebSocket
from redis import asyncio as aioredis

from app.core import get_logger
from app.schemas.ws import ErrorData, MessageType, WSMessage

logger = get_logger(__name__)

ROOM_CHANNEL_PREFIX = "game:room:"


class WSConnectionManager:
    """
    Manages WebSocket connections per room with Redis pub/sub integration.
    
    Each room has a set of active connections. Messages are published to Redis
    channels for distribution to other server instances.
    """

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.active_connections: dict[str, set[WebSocket]] = {}
        self.connection_player_map: dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, room_code: str, player_id: int):
        """
        Register a new WebSocket connection for a room.
        
        Args:
            websocket: WebSocket connection
            room_code: Room code
            player_id: Player ID
        """
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = set()
        self.active_connections[room_code].add(websocket)
        self.connection_player_map[websocket] = player_id
        logger.info(
            f"Player {player_id} connected to room {room_code}",
            extra={"player_id": player_id, "room_code": room_code},
        )

    def disconnect(self, websocket: WebSocket, room_code: str):
        """
        Remove a WebSocket connection from a room.
        
        Args:
            websocket: WebSocket connection
            room_code: Room code
        """
        player_id = self.connection_player_map.pop(websocket, None)
        if room_code in self.active_connections:
            self.active_connections[room_code].discard(websocket)
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]
        logger.info(
            f"Player {player_id} disconnected from room {room_code}",
            extra={"player_id": player_id, "room_code": room_code},
        )

    async def broadcast(
        self, room_code: str, message: WSMessage, exclude_websocket: WebSocket | None = None
    ):
        """
        Broadcast a message to all clients in a room and publish to Redis.
        
        Args:
            room_code: Room code
            message: Message to broadcast
            exclude_websocket: Optional connection to exclude from broadcast
        """
        if room_code not in self.active_connections:
            return

        message_json = message.model_dump_json()

        disconnected = set()
        for websocket in self.active_connections[room_code]:
            if exclude_websocket and websocket == exclude_websocket:
                continue
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(
                    f"Error sending message to websocket: {e}",
                    extra={"room_code": room_code},
                )
                disconnected.add(websocket)

        for ws in disconnected:
            self.disconnect(ws, room_code)

        channel = f"{ROOM_CHANNEL_PREFIX}{room_code}"
        try:
            await self.redis.publish(channel, message_json)
        except Exception as e:
            logger.error(
                f"Error publishing to Redis: {e}",
                extra={"room_code": room_code, "channel": channel},
            )

    async def send_personal(self, websocket: WebSocket, message: WSMessage):
        """
        Send a message to a specific connection.
        
        Args:
            websocket: Target WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_text(message.model_dump_json())
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def send_error(
        self, websocket: WebSocket, code: str, message: str
    ):
        """
        Send an error message to a connection.
        
        Args:
            websocket: Target WebSocket connection
            code: Error code
            message: Error message
        """
        error_msg = WSMessage(
            type=MessageType.ERROR,
            data=ErrorData(code=code, message=message).model_dump(),
        )
        await self.send_personal(websocket, error_msg)

    def get_room_connection_count(self, room_code: str) -> int:
        """
        Get the number of active connections in a room.
        
        Args:
            room_code: Room code
        
        Returns:
            Number of connected players
        """
        return len(self.active_connections.get(room_code, set()))
