import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.projectile import Projectile
    from app.models.room_membership import RoomMembership
    from app.models.tank_state import TankState


class RoomStatus(str, enum.Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    FINISHED = "finished"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus, native_enum=False, length=20),
        default=RoomStatus.WAITING,
        nullable=False,
        index=True,
    )
    max_players: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    memberships: Mapped[list["RoomMembership"]] = relationship(
        "RoomMembership", back_populates="room", cascade="all, delete-orphan"
    )
    tank_states: Mapped[list["TankState"]] = relationship(
        "TankState", back_populates="room", cascade="all, delete-orphan"
    )
    projectiles: Mapped[list["Projectile"]] = relationship(
        "Projectile", back_populates="room", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Room(id={self.id}, code='{self.code}', name='{self.name}', status='{self.status}')>"

    @property
    def current_players(self) -> int:
        return len(self.memberships)

    @property
    def is_full(self) -> bool:
        return self.current_players >= self.max_players

    @property
    def can_start(self) -> bool:
        return self.current_players >= 2 and self.status == RoomStatus.WAITING
