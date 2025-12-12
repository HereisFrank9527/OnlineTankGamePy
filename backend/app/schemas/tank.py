from datetime import datetime

from pydantic import BaseModel, Field


class TankStateBase(BaseModel):
    position_x: float = Field(default=0.0)
    position_y: float = Field(default=0.0)
    rotation: float = Field(default=0.0, ge=0.0, lt=360.0)


class TankStateCreate(TankStateBase):
    player_id: int
    room_id: int
    hp: int = Field(default=100, ge=0, le=100)
    max_hp: int = Field(default=100, ge=0, le=100)


class TankStateUpdate(BaseModel):
    position_x: float | None = None
    position_y: float | None = None
    rotation: float | None = Field(None, ge=0.0, lt=360.0)
    velocity_x: float | None = None
    velocity_y: float | None = None
    hp: int | None = Field(None, ge=0)


class TankStateResponse(TankStateBase):
    id: int
    player_id: int
    room_id: int
    hp: int
    max_hp: int
    velocity_x: float
    velocity_y: float
    is_alive: bool
    hp_percentage: float
    last_updated: datetime

    model_config = {"from_attributes": True}


class TankMovement(BaseModel):
    position_x: float
    position_y: float
    rotation: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0
