from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class PlayerBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class PlayerCreate(PlayerBase):
    password: str = Field(..., min_length=8, max_length=100)


class PlayerUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=100)


class PlayerStats(BaseModel):
    kills: int
    deaths: int
    wins: int
    losses: int
    games_played: int
    kd_ratio: float
    win_rate: float

    model_config = {"from_attributes": True}


class PlayerResponse(PlayerBase):
    id: int
    last_login_at: datetime | None
    login_count: int
    kills: int
    deaths: int
    wins: int
    losses: int
    games_played: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlayerDetail(PlayerResponse):
    kd_ratio: float
    win_rate: float


class PlayerInDB(PlayerResponse):
    hashed_password: str


class LeaderboardEntry(BaseModel):
    id: int
    username: str
    kills: int
    deaths: int
    wins: int
    losses: int
    games_played: int
    kd_ratio: float
    win_rate: float
    rank: int | None = None

    model_config = {"from_attributes": True}
