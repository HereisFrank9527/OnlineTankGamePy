from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.room import Room, RoomStatus
from app.models.room_membership import RoomMembership
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    def __init__(self, db: AsyncSession):
        super().__init__(Room, db)

    async def get_by_code(self, code: str) -> Room | None:
        result = await self.db.execute(select(Room).where(Room.code == code))
        return result.scalar_one_or_none()

    async def get_with_members(self, room_id: int) -> Room | None:
        result = await self.db.execute(
            select(Room)
            .where(Room.id == room_id)
            .options(selectinload(Room.memberships).selectinload(RoomMembership.player))
        )
        return result.scalar_one_or_none()

    async def get_by_status(
        self, status: RoomStatus, skip: int = 0, limit: int = 100
    ) -> list[Room]:
        result = await self.db.execute(
            select(Room).where(Room.status == status).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_available_rooms(self, skip: int = 0, limit: int = 100) -> list[Room]:
        result = await self.db.execute(
            select(Room)
            .where(Room.status == RoomStatus.WAITING)
            .options(selectinload(Room.memberships))
            .offset(skip)
            .limit(limit)
        )
        rooms = list(result.scalars().all())
        return [room for room in rooms if not room.is_full]

    async def get_player_room(self, player_id: int) -> Room | None:
        result = await self.db.execute(
            select(Room)
            .join(RoomMembership)
            .where(RoomMembership.player_id == player_id)
            .where(Room.status != RoomStatus.FINISHED)
        )
        return result.scalar_one_or_none()
