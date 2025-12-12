from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.room import Room


class Projectile(Base):
    __tablename__ = "projectiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    shooter_player_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    position_x: Mapped[float] = mapped_column(Float, nullable=False)
    position_y: Mapped[float] = mapped_column(Float, nullable=False)
    
    velocity_x: Mapped[float] = mapped_column(Float, nullable=False)
    velocity_y: Mapped[float] = mapped_column(Float, nullable=False)
    
    damage: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    room: Mapped["Room"] = relationship("Room", back_populates="projectiles")

    def __repr__(self) -> str:
        return f"<Projectile(id={self.id}, room_id={self.room_id}, shooter={self.shooter_player_id})>"
