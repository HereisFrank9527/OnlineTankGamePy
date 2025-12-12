"""Tests for room service and REST endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import RoomStatus
from app.services.room_service import RoomService


@pytest.mark.asyncio
async def test_room_service_create_room(db_session: AsyncSession):
    """Test creating a room via service."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room_data = RoomCreate(name="Test Room", max_players=4)
    room = await service.create_room(room_data, creator_id=1)

    assert room is not None
    assert room.name == "Test Room"
    assert room.max_players == 4
    assert room.status == RoomStatus.WAITING
    assert len(room.code) == 6
    assert room.code.isupper() or room.code[0].isdigit()


@pytest.mark.asyncio
async def test_room_service_get_room(db_session: AsyncSession):
    """Test retrieving a room via service."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    created = await service.create_room(RoomCreate(name="Get Test"), creator_id=1)

    retrieved = await service.get_room(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.code == created.code


@pytest.mark.asyncio
async def test_room_service_get_by_code(db_session: AsyncSession):
    """Test retrieving a room by code via service."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    created = await service.create_room(RoomCreate(name="Code Test"), creator_id=1)

    retrieved = await service.get_room_by_code(created.code)
    assert retrieved is not None
    assert retrieved.code == created.code


@pytest.mark.asyncio
async def test_room_service_join_room(db_session: AsyncSession):
    """Test joining a room via service."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room = await service.create_room(RoomCreate(name="Join Test"), creator_id=1)

    membership = await service.join_room(room.id, player_id=2)
    assert membership is not None
    assert membership.player_id == 2
    assert membership.room_id == room.id


@pytest.mark.asyncio
async def test_room_service_join_room_full(db_session: AsyncSession):
    """Test joining a full room raises error."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room = await service.create_room(RoomCreate(name="Full Test", max_players=2), creator_id=1)

    await service.join_room(room.id, player_id=2)

    with pytest.raises(ValueError, match="Room is full"):
        await service.join_room(room.id, player_id=3)


@pytest.mark.asyncio
async def test_room_service_join_room_already_member(db_session: AsyncSession):
    """Test joining same room twice raises error."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room = await service.create_room(RoomCreate(name="Duplicate Test"), creator_id=1)

    with pytest.raises(ValueError, match="Player already in room"):
        await service.join_room(room.id, player_id=1)


@pytest.mark.asyncio
async def test_room_service_leave_room(db_session: AsyncSession):
    """Test leaving a room via service."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room = await service.create_room(RoomCreate(name="Leave Test"), creator_id=1)

    await service.leave_room(room.id, player_id=1)

    retrieved = await service.get_room(room.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_room_service_set_player_ready(db_session: AsyncSession):
    """Test setting player ready status."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room = await service.create_room(RoomCreate(name="Ready Test"), creator_id=1)

    membership = await service.set_player_ready(room.id, player_id=1, is_ready=True)
    assert membership is not None
    assert membership.is_ready is True

    membership = await service.set_player_ready(room.id, player_id=1, is_ready=False)
    assert membership.is_ready is False


@pytest.mark.asyncio
async def test_room_service_start_game(db_session: AsyncSession):
    """Test starting a game."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room = await service.create_room(RoomCreate(name="Start Test"), creator_id=1)

    await service.join_room(room.id, player_id=2)

    await service.set_player_ready(room.id, player_id=1, is_ready=True)
    await service.set_player_ready(room.id, player_id=2, is_ready=True)

    started = await service.start_game(room.id)
    assert started.status == RoomStatus.ACTIVE


@pytest.mark.asyncio
async def test_room_service_start_game_not_ready(db_session: AsyncSession):
    """Test starting game when not all players ready fails."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)
    room = await service.create_room(RoomCreate(name="Not Ready Test"), creator_id=1)

    await service.join_room(room.id, player_id=2)
    await service.set_player_ready(room.id, player_id=1, is_ready=True)

    with pytest.raises(ValueError, match="Not all players are ready"):
        await service.start_game(room.id)


@pytest.mark.asyncio
async def test_room_service_get_available_rooms(db_session: AsyncSession):
    """Test getting available rooms."""
    from app.schemas.room import RoomCreate

    service = RoomService(db_session)

    await service.create_room(RoomCreate(name="Available 1"), creator_id=1)
    await service.create_room(RoomCreate(name="Available 2"), creator_id=2)

    available = await service.get_available_rooms()
    assert len(available) >= 2


@pytest.mark.asyncio
async def test_rest_list_rooms(client: AsyncClient, db_session: AsyncSession):
    """Test listing rooms via REST endpoint."""
    from app.schemas.auth import LoginRequest
    from app.schemas.room import RoomCreate
    from app.services.player_service import PlayerService
    from app.services.room_service import RoomService

    player_service = PlayerService(db_session)
    room_service = RoomService(db_session)

    from app.schemas.player import PlayerCreate

    player = await player_service.create_player(
        PlayerCreate(username="testuser", email="test@example.com", password="password123")
    )

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login.json()["access_token"]

    await room_service.create_room(RoomCreate(name="Test Room"), creator_id=player.id)

    response = await client.get("/api/v1/rooms", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) > 0


@pytest.mark.asyncio
async def test_rest_create_room(client: AsyncClient, db_session: AsyncSession):
    """Test creating room via REST endpoint."""
    from app.schemas.player import PlayerCreate
    from app.services.player_service import PlayerService

    player_service = PlayerService(db_session)
    player = await player_service.create_player(
        PlayerCreate(username="creator", email="creator@example.com", password="password123")
    )

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "creator", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/rooms",
        json={"name": "My Room", "max_players": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    room = response.json()
    assert room["name"] == "My Room"
    assert room["max_players"] == 4
    assert len(room["code"]) == 6


@pytest.mark.asyncio
async def test_rest_get_room(client: AsyncClient, db_session: AsyncSession):
    """Test getting room details via REST endpoint."""
    from app.schemas.player import PlayerCreate
    from app.schemas.room import RoomCreate
    from app.services.player_service import PlayerService
    from app.services.room_service import RoomService

    player_service = PlayerService(db_session)
    room_service = RoomService(db_session)

    player = await player_service.create_player(
        PlayerCreate(username="getter", email="getter@example.com", password="password123")
    )
    room = await room_service.create_room(RoomCreate(name="Get Test"), creator_id=player.id)

    response = await client.get(f"/api/v1/rooms/{room.code}")
    assert response.status_code == 200
    room_data = response.json()
    assert room_data["code"] == room.code
    assert room_data["name"] == "Get Test"


@pytest.mark.asyncio
async def test_rest_join_room(client: AsyncClient, db_session: AsyncSession):
    """Test joining room via REST endpoint."""
    from app.schemas.player import PlayerCreate
    from app.schemas.room import RoomCreate
    from app.services.player_service import PlayerService
    from app.services.room_service import RoomService

    player_service = PlayerService(db_session)
    room_service = RoomService(db_session)

    player1 = await player_service.create_player(
        PlayerCreate(username="player1", email="player1@example.com", password="password123")
    )
    player2 = await player_service.create_player(
        PlayerCreate(username="player2", email="player2@example.com", password="password123")
    )
    room = await room_service.create_room(RoomCreate(name="Join Room"), creator_id=player1.id)

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "player2", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        f"/api/v1/rooms/{room.code}/join",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    joined_room = response.json()
    assert joined_room["current_players"] == 2


@pytest.mark.asyncio
async def test_rest_join_full_room(client: AsyncClient, db_session: AsyncSession):
    """Test joining full room returns error."""
    from app.schemas.player import PlayerCreate
    from app.schemas.room import RoomCreate
    from app.services.player_service import PlayerService
    from app.services.room_service import RoomService

    player_service = PlayerService(db_session)
    room_service = RoomService(db_session)

    player1 = await player_service.create_player(
        PlayerCreate(username="full1", email="full1@example.com", password="password123")
    )
    player2 = await player_service.create_player(
        PlayerCreate(username="full2", email="full2@example.com", password="password123")
    )
    player3 = await player_service.create_player(
        PlayerCreate(username="full3", email="full3@example.com", password="password123")
    )

    room = await room_service.create_room(
        RoomCreate(name="Full Room", max_players=2), creator_id=player1.id
    )
    await room_service.join_room(room.id, player_id=player2.id)

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "full3", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        f"/api/v1/rooms/{room.code}/join",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rest_leave_room(client: AsyncClient, db_session: AsyncSession):
    """Test leaving room via REST endpoint."""
    from app.schemas.player import PlayerCreate
    from app.schemas.room import RoomCreate
    from app.services.player_service import PlayerService
    from app.services.room_service import RoomService

    player_service = PlayerService(db_session)
    room_service = RoomService(db_session)

    player = await player_service.create_player(
        PlayerCreate(username="leaver", email="leaver@example.com", password="password123")
    )
    room = await room_service.create_room(RoomCreate(name="Leave Room"), creator_id=player.id)

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "leaver", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        f"/api/v1/rooms/{room.code}/leave",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    get_room = await client.get(f"/api/v1/rooms/{room.code}")
    assert get_room.status_code == 404


@pytest.mark.asyncio
async def test_rest_set_ready(client: AsyncClient, db_session: AsyncSession):
    """Test setting ready status via REST endpoint."""
    from app.schemas.player import PlayerCreate
    from app.schemas.room import RoomCreate
    from app.services.player_service import PlayerService
    from app.services.room_service import RoomService

    player_service = PlayerService(db_session)
    room_service = RoomService(db_session)

    player = await player_service.create_player(
        PlayerCreate(username="ready_player", email="ready@example.com", password="password123")
    )
    room = await room_service.create_room(RoomCreate(name="Ready Room"), creator_id=player.id)

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "ready_player", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        f"/api/v1/rooms/{room.code}/ready/true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_rest_start_game(client: AsyncClient, db_session: AsyncSession):
    """Test starting game via REST endpoint."""
    from app.schemas.player import PlayerCreate
    from app.schemas.room import RoomCreate
    from app.services.player_service import PlayerService
    from app.services.room_service import RoomService

    player_service = PlayerService(db_session)
    room_service = RoomService(db_session)

    player1 = await player_service.create_player(
        PlayerCreate(username="start1", email="start1@example.com", password="password123")
    )
    player2 = await player_service.create_player(
        PlayerCreate(username="start2", email="start2@example.com", password="password123")
    )

    room = await room_service.create_room(RoomCreate(name="Start Room"), creator_id=player1.id)
    await room_service.join_room(room.id, player_id=player2.id)

    await room_service.set_player_ready(room.id, player_id=player1.id, is_ready=True)
    await room_service.set_player_ready(room.id, player_id=player2.id, is_ready=True)

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "start1", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        f"/api/v1/rooms/{room.code}/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    started_room = response.json()
    assert started_room["status"] == "active"
