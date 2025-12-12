from datetime import datetime

from pydantic import BaseModel, Field


class ProjectileBase(BaseModel):
    position_x: float
    position_y: float
    velocity_x: float
    velocity_y: float


class ProjectileCreate(ProjectileBase):
    room_id: int
    shooter_player_id: int
    damage: int = Field(default=25, ge=1, le=100)


class ProjectileResponse(ProjectileBase):
    id: int
    room_id: int
    shooter_player_id: int
    damage: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectileShoot(BaseModel):
    direction_x: float
    direction_y: float
    speed: float = Field(default=10.0, ge=1.0, le=50.0)
