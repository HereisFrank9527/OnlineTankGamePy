from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player import Player
from app.repositories.base import BaseRepository


class PlayerRepository(BaseRepository[Player]):
    def __init__(self, db: AsyncSession):
        super().__init__(Player, db)

    async def get_by_username(self, username: str) -> Player | None:
        result = await self.db.execute(select(Player).where(Player.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Player | None:
        result = await self.db.execute(select(Player).where(Player.email == email))
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> Player | None:
        result = await self.db.execute(
            select(Player).where((Player.username == identifier) | (Player.email == identifier))
        )
        return result.scalar_one_or_none()

    async def get_leaderboard(
        self, order_by: str = "kills", skip: int = 0, limit: int = 100
    ) -> list[Player]:
        order_column = getattr(Player, order_by, Player.kills)
        result = await self.db.execute(
            select(Player).order_by(order_column.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_top_by_kd(self, limit: int = 10) -> list[Player]:
        result = await self.db.execute(
            select(Player)
            .where(Player.deaths > 0)
            .order_by((Player.kills / Player.deaths).desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_top_by_wins(self, limit: int = 10) -> list[Player]:
        result = await self.db.execute(
            select(Player).order_by(Player.wins.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_count(self) -> int:
        result = await self.db.execute(select(func.count(Player.id)))
        return result.scalar_one()

    async def update_stats(
        self,
        player: Player,
        kills: int = 0,
        deaths: int = 0,
        wins: int = 0,
        losses: int = 0,
    ) -> Player:
        player.kills += kills
        player.deaths += deaths
        player.wins += wins
        player.losses += losses
        player.games_played += 1 if (wins + losses) > 0 else 0
        return await self.update(player)
