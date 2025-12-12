from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_membership import RoomMembership
from app.repositories.base import BaseRepository


class RoomMembershipRepository(BaseRepository[RoomMembership]):
    def __init__(self, db: AsyncSession):
        super().__init__(RoomMembership, db)

    async def get_by_player_and_room(
        self, player_id: int, room_id: int
    ) -> RoomMembership | None:
        result = await self.db.execute(
            select(RoomMembership).where(
                RoomMembership.player_id == player_id, RoomMembership.room_id == room_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_room(self, room_id: int) -> list[RoomMembership]:
        result = await self.db.execute(
            select(RoomMembership).where(RoomMembership.room_id == room_id)
        )
        return list(result.scalars().all())

    async def get_by_player(self, player_id: int) -> list[RoomMembership]:
        result = await self.db.execute(
            select(RoomMembership).where(RoomMembership.player_id == player_id)
        )
        return list(result.scalars().all())

    async def count_by_room(self, room_id: int) -> int:
        result = await self.db.execute(
            select(RoomMembership).where(RoomMembership.room_id == room_id)
        )
        return len(list(result.scalars().all()))

    async def delete_by_player_and_room(self, player_id: int, room_id: int) -> None:
        membership = await self.get_by_player_and_room(player_id, room_id)
        if membership:
            await self.delete(membership)
