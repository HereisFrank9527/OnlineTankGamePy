from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.room import Room


class RoomMembership(Base):
    __tablename__ = "room_memberships"
    __table_args__ = (
        UniqueConstraint("player_id", "room_id", name="uq_player_room"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tank_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    player: Mapped["Player"] = relationship("Player", back_populates="room_memberships")
    room: Mapped["Room"] = relationship("Room", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<RoomMembership(id={self.id}, player_id={self.player_id}, room_id={self.room_id})>"
