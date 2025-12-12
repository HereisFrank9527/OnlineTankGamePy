from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.room import Room


class TankState(Base):
    __tablename__ = "tank_states"
    __table_args__ = (
        UniqueConstraint("player_id", "room_id", name="uq_tank_player_room"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    position_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rotation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    hp: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    
    velocity_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    velocity_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    player: Mapped["Player"] = relationship("Player", back_populates="tank_states")
    room: Mapped["Room"] = relationship("Room", back_populates="tank_states")

    def __repr__(self) -> str:
        return f"<TankState(id={self.id}, player_id={self.player_id}, room_id={self.room_id}, hp={self.hp})>"

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def hp_percentage(self) -> float:
        if self.max_hp == 0:
            return 0.0
        return round((self.hp / self.max_hp) * 100, 2)
