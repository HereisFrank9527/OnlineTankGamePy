"""
WebSocket message protocol for real-time game synchronization.

Message Flow:
- Client connects to /ws/game/{room_code}
- Server authenticates via query param token
- Client/server exchange JSON messages
- Messages are broadcast to all room participants
- Redis pub/sub ensures horizontal scaling across multiple server instances

Message Types:
  join: Player enters room (broadcast to all)
  leave: Player exits room (broadcast to all)
  tank_state_update: Tank position/rotation sync
  fire: Projectile creation
  scoreboard: Periodic leaderboard update
  error: Server error response
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """WebSocket message event types."""

    JOIN = "join"
    LEAVE = "leave"
    TANK_STATE_UPDATE = "tank_state_update"
    FIRE = "fire"
    SCOREBOARD = "scoreboard"
    ERROR = "error"


class WSMessage(BaseModel):
    """Base WebSocket message structure."""

    type: MessageType
    data: dict[str, Any] = Field(default_factory=dict)


class PlayerJoinData(BaseModel):
    """Data payload for join event."""

    player_id: int
    username: str
    tank_color: str | None = None


class PlayerLeaveData(BaseModel):
    """Data payload for leave event."""

    player_id: int
    username: str


class TankStateUpdateData(BaseModel):
    """Data payload for tank state update."""

    player_id: int
    position_x: float
    position_y: float
    rotation: float
    velocity_x: float
    velocity_y: float
    hp: int


class FireData(BaseModel):
    """Data payload for projectile fire event."""

    player_id: int
    projectile_id: int
    start_x: float
    start_y: float
    direction_x: float
    direction_y: float
    damage: int


class ScoreboardEntry(BaseModel):
    """Entry in scoreboard."""

    player_id: int
    username: str
    kills: int
    deaths: int
    hp: int


class ScoreboardData(BaseModel):
    """Data payload for scoreboard update."""

    entries: list[ScoreboardEntry]


class ErrorData(BaseModel):
    """Data payload for error messages."""

    code: str
    message: str
