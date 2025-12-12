from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projectile import Projectile
from app.models.tank_state import TankState
from app.repositories.projectile import ProjectileRepository
from app.repositories.tank_state import TankStateRepository
from app.schemas.projectile import ProjectileCreate
from app.schemas.tank import TankMovement, TankStateCreate, TankStateUpdate


class GameService:
    def __init__(self, db: AsyncSession):
        self.tank_repo = TankStateRepository(db)
        self.projectile_repo = ProjectileRepository(db)

    async def create_tank_state(self, tank_data: TankStateCreate) -> TankState:
        existing = await self.tank_repo.get_by_player_and_room(
            tank_data.player_id, tank_data.room_id
        )
        if existing:
            raise ValueError("Tank state already exists for this player in this room")

        tank = TankState(
            player_id=tank_data.player_id,
            room_id=tank_data.room_id,
            position_x=tank_data.position_x,
            position_y=tank_data.position_y,
            rotation=tank_data.rotation,
            hp=tank_data.hp,
            max_hp=tank_data.max_hp,
        )
        return await self.tank_repo.create(tank)

    async def get_tank_state(
        self, player_id: int, room_id: int
    ) -> TankState | None:
        return await self.tank_repo.get_by_player_and_room(player_id, room_id)

    async def get_room_tank_states(self, room_id: int) -> list[TankState]:
        return await self.tank_repo.get_by_room(room_id)

    async def update_tank_movement(
        self, tank: TankState, movement: TankMovement
    ) -> TankState:
        tank.position_x = movement.position_x
        tank.position_y = movement.position_y
        tank.rotation = movement.rotation
        tank.velocity_x = movement.velocity_x
        tank.velocity_y = movement.velocity_y
        return await self.tank_repo.update(tank)

    async def update_tank_state(
        self, tank: TankState, update_data: TankStateUpdate
    ) -> TankState:
        if update_data.position_x is not None:
            tank.position_x = update_data.position_x
        if update_data.position_y is not None:
            tank.position_y = update_data.position_y
        if update_data.rotation is not None:
            tank.rotation = update_data.rotation
        if update_data.velocity_x is not None:
            tank.velocity_x = update_data.velocity_x
        if update_data.velocity_y is not None:
            tank.velocity_y = update_data.velocity_y
        if update_data.hp is not None:
            tank.hp = max(0, min(update_data.hp, tank.max_hp))

        return await self.tank_repo.update(tank)

    async def damage_tank(self, tank: TankState, damage: int) -> TankState:
        tank.hp = max(0, tank.hp - damage)
        return await self.tank_repo.update(tank)

    async def create_projectile(self, projectile_data: ProjectileCreate) -> Projectile:
        projectile = Projectile(
            room_id=projectile_data.room_id,
            shooter_player_id=projectile_data.shooter_player_id,
            position_x=projectile_data.position_x,
            position_y=projectile_data.position_y,
            velocity_x=projectile_data.velocity_x,
            velocity_y=projectile_data.velocity_y,
            damage=projectile_data.damage,
        )
        return await self.projectile_repo.create(projectile)

    async def get_room_projectiles(self, room_id: int) -> list[Projectile]:
        return await self.projectile_repo.get_by_room(room_id)

    async def delete_projectile(self, projectile: Projectile) -> None:
        await self.projectile_repo.delete(projectile)

    async def cleanup_old_projectiles(self, room_id: int, max_age_seconds: int = 10) -> int:
        return await self.projectile_repo.delete_old_projectiles(room_id, max_age_seconds)
