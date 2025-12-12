# Database Documentation

## Overview

This document describes the persistence layer for the Tank Battle game backend, including database models, migrations, and usage.

## Database Schema

### Tables

#### Players
Stores user credentials and game statistics for the leaderboard.

- `id`: Primary key
- `username`: Unique username (indexed)
- `email`: Unique email address (indexed)
- `hashed_password`: Bcrypt hashed password
- `kills`, `deaths`, `wins`, `losses`, `games_played`: Statistics
- `created_at`, `updated_at`: Timestamps

#### Rooms
Game rooms that players can join and play in.

- `id`: Primary key
- `code`: Unique 6-character room code (indexed)
- `name`: Room name
- `status`: Enum (WAITING, ACTIVE, FINISHED) - indexed
- `max_players`: Maximum number of players (default: 8)
- `created_at`, `updated_at`: Timestamps

#### RoomMemberships
Junction table linking players to rooms.

- `id`: Primary key
- `player_id`: Foreign key to players (indexed)
- `room_id`: Foreign key to rooms (indexed)
- `is_ready`: Boolean flag for player readiness
- `tank_color`: Optional tank color assignment
- `joined_at`: Timestamp
- Unique constraint on (player_id, room_id)

#### TankStates
Real-time tank state for each player in a room.

- `id`: Primary key
- `player_id`: Foreign key to players (indexed)
- `room_id`: Foreign key to rooms (indexed)
- `position_x`, `position_y`: Tank position
- `rotation`: Tank rotation (0-360 degrees)
- `hp`, `max_hp`: Hit points
- `velocity_x`, `velocity_y`: Movement velocity
- `last_updated`: Timestamp
- Unique constraint on (player_id, room_id)

#### Projectiles
Active projectiles/bullets in rooms.

- `id`: Primary key
- `room_id`: Foreign key to rooms (indexed)
- `shooter_player_id`: Player who shot the projectile
- `position_x`, `position_y`: Projectile position
- `velocity_x`, `velocity_y`: Movement velocity
- `damage`: Damage amount (default: 25)
- `created_at`: Timestamp

## Migrations

### Creating Migrations

```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
alembic upgrade head
```

### Rolling Back

```bash
alembic downgrade -1
```

## Models

All SQLAlchemy models are located in `app/models/`:

- `player.py`: Player model
- `room.py`: Room and RoomStatus enum
- `room_membership.py`: RoomMembership model
- `tank_state.py`: TankState model
- `projectile.py`: Projectile model

## Schemas

Pydantic schemas for request/response validation are in `app/schemas/`:

- `player.py`: Player CRUD schemas, LeaderboardEntry
- `room.py`: Room and RoomMembership schemas
- `tank.py`: TankState and TankMovement schemas
- `projectile.py`: Projectile schemas

## Repositories

Repository pattern for database access in `app/repositories/`:

- `player.py`: PlayerRepository - player CRUD, leaderboard queries
- `room.py`: RoomRepository - room CRUD, filtering by status
- `room_membership.py`: RoomMembershipRepository - membership management
- `tank_state.py`: TankStateRepository - tank state management
- `projectile.py`: ProjectileRepository - projectile management

### Repository Usage Example

```python
from app.repositories.player import PlayerRepository

async def get_top_players(db: AsyncSession):
    player_repo = PlayerRepository(db)
    top_players = await player_repo.get_leaderboard(order_by="kills", limit=10)
    return top_players
```

## Services

Business logic layer in `app/services/`:

- `player_service.py`: Player operations (registration, authentication, stats)
- `room_service.py`: Room operations (create, join, leave, start game)
- `game_service.py`: Game operations (tank movement, projectiles, damage)

### Service Usage Example

```python
from app.services.room_service import RoomService
from app.schemas.room import RoomCreate

async def create_game_room(db: AsyncSession, creator_id: int):
    room_service = RoomService(db)
    room_data = RoomCreate(name="My Battle Room", max_players=4)
    room = await room_service.create_room(room_data, creator_id)
    return room
```

## Seeding

To populate the database with sample data:

```bash
cd backend
source .venv/bin/activate
python seed.py
```

This creates:
- 5 sample players (password: `password123`)
- 3 sample rooms with various statuses
- Room memberships and tank states
- Map layout reference

Sample login: `username='tank_master'`, `password='password123'`

## Map Layout

The seed script includes a reference map layout:

- **Name**: Classic Arena
- **Size**: 800x600 pixels
- **Spawn Positions**: 8 predefined positions
- **Obstacles**: 7 walls and blocks
- **Power-ups**: 4 locations (health, speed, damage)

This data is logged during seeding and can be used to initialize gameplay.

## Database Session Dependency

FastAPI dependency injection for database sessions:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

@router.get("/example")
async def example_endpoint(db: AsyncSession = Depends(get_db)):
    # Use db session here
    pass
```

## Connection String

Format: `postgresql+asyncpg://user:password@host:port/dbname`

Default (from .env.example):
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tank_game
```

## Running with Docker

Start PostgreSQL and Redis:

```bash
cd backend
docker compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

## Database Management

### Connect to PostgreSQL

```bash
docker exec -it backend_postgres psql -U postgres -d tank_game
```

### Useful Queries

```sql
-- List all players
SELECT username, kills, deaths, wins FROM players ORDER BY kills DESC;

-- List active rooms
SELECT code, name, status FROM rooms WHERE status = 'ACTIVE';

-- Count players per room
SELECT r.code, r.name, COUNT(rm.id) as player_count
FROM rooms r
LEFT JOIN room_memberships rm ON r.id = rm.room_id
GROUP BY r.id, r.code, r.name;

-- Get tank states for a room
SELECT p.username, ts.position_x, ts.position_y, ts.hp
FROM tank_states ts
JOIN players p ON ts.player_id = p.id
WHERE ts.room_id = 1;
```

## Indexes

The following indexes are created for performance:

- `players.username` (unique)
- `players.email` (unique)
- `rooms.code` (unique)
- `rooms.status`
- `room_memberships.player_id`
- `room_memberships.room_id`
- `tank_states.player_id`
- `tank_states.room_id`
- `projectiles.room_id`

## Cascade Deletes

Foreign key constraints with CASCADE delete:

- Deleting a player removes all their memberships and tank states
- Deleting a room removes all memberships, tank states, and projectiles
- This keeps the database clean and prevents orphaned records
