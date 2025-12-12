from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tank_state import TankState
from app.repositories.base import BaseRepository


class TankStateRepository(BaseRepository[TankState]):
    def __init__(self, db: AsyncSession):
        super().__init__(TankState, db)

    async def get_by_player_and_room(
        self, player_id: int, room_id: int
    ) -> TankState | None:
        result = await self.db.execute(
            select(TankState).where(
                TankState.player_id == player_id, TankState.room_id == room_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_room(self, room_id: int) -> list[TankState]:
        result = await self.db.execute(
            select(TankState).where(TankState.room_id == room_id)
        )
        return list(result.scalars().all())

    async def get_alive_by_room(self, room_id: int) -> list[TankState]:
        result = await self.db.execute(
            select(TankState).where(TankState.room_id == room_id, TankState.hp > 0)
        )
        return list(result.scalars().all())

    async def delete_by_room(self, room_id: int) -> None:
        tanks = await self.get_by_room(room_id)
        for tank in tanks:
            await self.delete(tank)
