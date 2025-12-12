import asyncio
import random
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger, setup_logging
from app.core.security import get_password_hash
from app.models.player import Player
from app.models.room import Room, RoomStatus
from app.models.room_membership import RoomMembership
from app.models.tank_state import TankState

setup_logging()
logger = get_logger(__name__)

SAMPLE_PLAYERS = [
    {"username": "tank_master", "email": "tank@example.com", "password": "password123"},
    {"username": "battle_pro", "email": "battle@example.com", "password": "password123"},
    {"username": "steel_warrior", "email": "steel@example.com", "password": "password123"},
    {"username": "cannon_king", "email": "cannon@example.com", "password": "password123"},
    {"username": "armor_ace", "email": "armor@example.com", "password": "password123"},
]

TANK_COLORS = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "pink"]

SPAWN_POSITIONS = [
    (100.0, 100.0),
    (700.0, 100.0),
    (100.0, 500.0),
    (700.0, 500.0),
    (400.0, 100.0),
    (400.0, 500.0),
    (100.0, 300.0),
    (700.0, 300.0),
]


async def seed_players(db: AsyncSession) -> list[Player]:
    logger.info("Seeding sample players...")
    players = []
    
    for i, player_data in enumerate(SAMPLE_PLAYERS):
        player = Player(
            username=player_data["username"],
            email=player_data["email"],
            hashed_password=get_password_hash(player_data["password"]),
            kills=random.randint(0, 50),
            deaths=random.randint(0, 40),
            wins=random.randint(0, 20),
            losses=random.randint(0, 15),
            games_played=random.randint(5, 35),
        )
        db.add(player)
        players.append(player)
    
    await db.commit()
    
    for player in players:
        await db.refresh(player)
    
    logger.info(f"Created {len(players)} sample players")
    return players


async def seed_rooms(db: AsyncSession, players: list[Player]) -> list[Room]:
    logger.info("Seeding sample rooms...")
    
    room1 = Room(
        code="ROOM01",
        name="Beginner Arena",
        status=RoomStatus.WAITING,
        max_players=8,
    )
    db.add(room1)
    
    room2 = Room(
        code="ROOM02",
        name="Pro Battle Zone",
        status=RoomStatus.ACTIVE,
        max_players=4,
    )
    db.add(room2)
    
    room3 = Room(
        code="ROOM03",
        name="Elite Warfare",
        status=RoomStatus.WAITING,
        max_players=6,
    )
    db.add(room3)
    
    await db.commit()
    await db.refresh(room1)
    await db.refresh(room2)
    await db.refresh(room3)
    
    membership1 = RoomMembership(
        player_id=players[0].id,
        room_id=room1.id,
        is_ready=True,
        tank_color=TANK_COLORS[0],
    )
    db.add(membership1)
    
    membership2 = RoomMembership(
        player_id=players[1].id,
        room_id=room1.id,
        is_ready=False,
        tank_color=TANK_COLORS[1],
    )
    db.add(membership2)
    
    membership3 = RoomMembership(
        player_id=players[2].id,
        room_id=room2.id,
        is_ready=True,
        tank_color=TANK_COLORS[0],
    )
    db.add(membership3)
    
    membership4 = RoomMembership(
        player_id=players[3].id,
        room_id=room2.id,
        is_ready=True,
        tank_color=TANK_COLORS[1],
    )
    db.add(membership4)
    
    await db.commit()
    
    logger.info(f"Created 3 sample rooms with memberships")
    return [room1, room2, room3]


async def seed_tank_states(db: AsyncSession, players: list[Player], room: Room) -> None:
    logger.info(f"Seeding tank states for room {room.code}...")
    
    tank1 = TankState(
        player_id=players[2].id,
        room_id=room.id,
        position_x=SPAWN_POSITIONS[0][0],
        position_y=SPAWN_POSITIONS[0][1],
        rotation=45.0,
        hp=100,
        max_hp=100,
    )
    db.add(tank1)
    
    tank2 = TankState(
        player_id=players[3].id,
        room_id=room.id,
        position_x=SPAWN_POSITIONS[1][0],
        position_y=SPAWN_POSITIONS[1][1],
        rotation=225.0,
        hp=85,
        max_hp=100,
    )
    db.add(tank2)
    
    await db.commit()
    logger.info(f"Created tank states for active room")


async def create_map_layout_reference() -> dict:
    map_layout = {
        "name": "Classic Arena",
        "width": 800,
        "height": 600,
        "spawn_positions": SPAWN_POSITIONS,
        "obstacles": [
            {"type": "wall", "x": 200, "y": 200, "width": 100, "height": 20},
            {"type": "wall", "x": 500, "y": 200, "width": 100, "height": 20},
            {"type": "wall", "x": 200, "y": 400, "width": 100, "height": 20},
            {"type": "wall", "x": 500, "y": 400, "width": 100, "height": 20},
            {"type": "wall", "x": 350, "y": 250, "width": 20, "height": 100},
            {"type": "wall", "x": 450, "y": 250, "width": 20, "height": 100},
            {"type": "block", "x": 400, "y": 300, "width": 50, "height": 50},
        ],
        "power_ups": [
            {"type": "health", "x": 100, "y": 300},
            {"type": "health", "x": 700, "y": 300},
            {"type": "speed", "x": 400, "y": 100},
            {"type": "damage", "x": 400, "y": 500},
        ],
    }
    
    logger.info("Map layout reference created")
    logger.info(f"Map: {map_layout['name']}")
    logger.info(f"Size: {map_layout['width']}x{map_layout['height']}")
    logger.info(f"Spawn positions: {len(map_layout['spawn_positions'])}")
    logger.info(f"Obstacles: {len(map_layout['obstacles'])}")
    logger.info(f"Power-ups: {len(map_layout['power_ups'])}")
    
    return map_layout


async def main():
    logger.info("Starting database seeding...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    async with AsyncSessionLocal() as db:
        try:
            players = await seed_players(db)
            rooms = await seed_rooms(db, players)
            
            active_room = next((r for r in rooms if r.status == RoomStatus.ACTIVE), None)
            if active_room:
                await seed_tank_states(db, players, active_room)
            
            map_layout = await create_map_layout_reference()
            
            logger.info("Database seeding completed successfully!")
            logger.info("\n" + "=" * 60)
            logger.info("SAMPLE DATA SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Players created: {len(players)}")
            logger.info(f"Rooms created: {len(rooms)}")
            logger.info(f"Sample login: username='tank_master', password='password123'")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
