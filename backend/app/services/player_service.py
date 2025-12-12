from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.player import Player
from app.repositories.player import PlayerRepository
from app.schemas.player import PlayerCreate, PlayerUpdate


class PlayerService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerRepository(db)

    async def create_player(self, player_data: PlayerCreate) -> Player:
        existing_username = await self.repo.get_by_username(player_data.username)
        if existing_username:
            raise ValueError("Username already exists")

        existing_email = await self.repo.get_by_email(player_data.email)
        if existing_email:
            raise ValueError("Email already exists")

        player = Player(
            username=player_data.username,
            email=player_data.email,
            hashed_password=get_password_hash(player_data.password),
        )
        return await self.repo.create(player)

    async def get_player(self, player_id: int) -> Player | None:
        return await self.repo.get(player_id)

    async def get_player_by_username(self, username: str) -> Player | None:
        return await self.repo.get_by_username(username)

    async def authenticate_player(self, identifier: str, password: str) -> Player | None:
        player = await self.repo.get_by_username_or_email(identifier)
        if not player:
            return None
        if not verify_password(password, player.hashed_password):
            return None
        return player

    async def record_login(self, player: Player) -> Player:
        player.last_login_at = datetime.utcnow()
        player.login_count += 1
        return await self.repo.update(player)

    async def update_player(self, player: Player, player_data: PlayerUpdate) -> Player:
        if player_data.email:
            existing_email = await self.repo.get_by_email(player_data.email)
            if existing_email and existing_email.id != player.id:
                raise ValueError("Email already exists")
            player.email = player_data.email

        if player_data.password:
            player.hashed_password = get_password_hash(player_data.password)

        return await self.repo.update(player)

    async def get_leaderboard(
        self, order_by: str = "kills", skip: int = 0, limit: int = 100
    ) -> list[Player]:
        return await self.repo.get_leaderboard(order_by, skip, limit)

    async def update_player_stats(
        self, player: Player, kills: int = 0, deaths: int = 0, wins: int = 0, losses: int = 0
    ) -> Player:
        return await self.repo.update_stats(player, kills, deaths, wins, losses)
