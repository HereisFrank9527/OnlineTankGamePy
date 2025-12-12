from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projectile import Projectile
from app.repositories.base import BaseRepository


class ProjectileRepository(BaseRepository[Projectile]):
    def __init__(self, db: AsyncSession):
        super().__init__(Projectile, db)

    async def get_by_room(self, room_id: int) -> list[Projectile]:
        result = await self.db.execute(
            select(Projectile).where(Projectile.room_id == room_id)
        )
        return list(result.scalars().all())

    async def get_by_shooter(self, shooter_player_id: int) -> list[Projectile]:
        result = await self.db.execute(
            select(Projectile).where(Projectile.shooter_player_id == shooter_player_id)
        )
        return list(result.scalars().all())

    async def delete_old_projectiles(self, room_id: int, max_age_seconds: int = 10) -> int:
        cutoff_time = datetime.utcnow() - timedelta(seconds=max_age_seconds)
        projectiles = await self.get_by_room(room_id)
        deleted_count = 0
        for projectile in projectiles:
            if projectile.created_at < cutoff_time:
                await self.delete(projectile)
                deleted_count += 1
        return deleted_count

    async def delete_by_room(self, room_id: int) -> None:
        projectiles = await self.get_by_room(room_id)
        for projectile in projectiles:
            await self.delete(projectile)
