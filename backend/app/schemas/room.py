from datetime import datetime

from pydantic import BaseModel, Field

from app.models.room import RoomStatus


class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class RoomCreate(RoomBase):
    max_players: int = Field(default=8, ge=2, le=8)


class RoomUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    status: RoomStatus | None = None
    max_players: int | None = Field(None, ge=2, le=8)


class RoomResponse(RoomBase):
    id: int
    code: str
    status: RoomStatus
    max_players: int
    current_players: int
    is_full: bool
    can_start: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoomMembershipBase(BaseModel):
    is_ready: bool = False
    tank_color: str | None = None


class RoomMembershipCreate(RoomMembershipBase):
    pass


class RoomMembershipUpdate(BaseModel):
    is_ready: bool | None = None
    tank_color: str | None = None


class RoomMembershipResponse(RoomMembershipBase):
    id: int
    player_id: int
    room_id: int
    joined_at: datetime

    model_config = {"from_attributes": True}


class RoomMemberDetail(RoomMembershipResponse):
    player_username: str | None = None


class RoomDetail(RoomResponse):
    members: list[RoomMemberDetail] = []
