import random
import string

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room, RoomStatus
from app.models.room_membership import RoomMembership
from app.repositories.room import RoomRepository
from app.repositories.room_membership import RoomMembershipRepository
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:
    def __init__(self, db: AsyncSession):
        self.room_repo = RoomRepository(db)
        self.membership_repo = RoomMembershipRepository(db)

    def _generate_room_code(self) -> str:
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    async def create_room(self, room_data: RoomCreate, creator_id: int) -> Room:
        code = self._generate_room_code()
        while await self.room_repo.get_by_code(code):
            code = self._generate_room_code()

        room = Room(
            code=code,
            name=room_data.name,
            max_players=room_data.max_players,
            status=RoomStatus.WAITING,
        )
        room = await self.room_repo.create(room)

        membership = RoomMembership(player_id=creator_id, room_id=room.id)
        await self.membership_repo.create(membership)

        return room

    async def get_room(self, room_id: int) -> Room | None:
        return await self.room_repo.get(room_id)

    async def get_room_by_code(self, code: str) -> Room | None:
        return await self.room_repo.get_by_code(code)

    async def get_room_with_members(self, room_id: int) -> Room | None:
        return await self.room_repo.get_with_members(room_id)

    async def update_room(self, room: Room, room_data: RoomUpdate) -> Room:
        if room_data.name is not None:
            room.name = room_data.name
        if room_data.status is not None:
            room.status = room_data.status
        if room_data.max_players is not None:
            room.max_players = room_data.max_players

        return await self.room_repo.update(room)

    async def delete_room(self, room: Room) -> None:
        await self.room_repo.delete(room)

    async def get_available_rooms(self, skip: int = 0, limit: int = 100) -> list[Room]:
        return await self.room_repo.get_available_rooms(skip, limit)

    async def join_room(self, room_id: int, player_id: int) -> RoomMembership:
        room = await self.room_repo.get(room_id)
        if not room:
            raise ValueError("Room not found")

        if room.is_full:
            raise ValueError("Room is full")

        if room.status != RoomStatus.WAITING:
            raise ValueError("Room is not accepting new players")

        existing = await self.membership_repo.get_by_player_and_room(player_id, room_id)
        if existing:
            raise ValueError("Player already in room")

        membership = RoomMembership(player_id=player_id, room_id=room_id)
        return await self.membership_repo.create(membership)

    async def leave_room(self, room_id: int, player_id: int) -> None:
        await self.membership_repo.delete_by_player_and_room(player_id, room_id)

        members_count = await self.membership_repo.count_by_room(room_id)
        if members_count == 0:
            room = await self.room_repo.get(room_id)
            if room:
                await self.room_repo.delete(room)

    async def set_player_ready(
        self, room_id: int, player_id: int, is_ready: bool
    ) -> RoomMembership:
        membership = await self.membership_repo.get_by_player_and_room(player_id, room_id)
        if not membership:
            raise ValueError("Player not in room")

        membership.is_ready = is_ready
        return await self.membership_repo.update(membership)

    async def start_game(self, room_id: int) -> Room:
        room = await self.room_repo.get(room_id)
        if not room:
            raise ValueError("Room not found")

        if not room.can_start:
            raise ValueError("Room cannot be started")

        memberships = await self.membership_repo.get_by_room(room_id)
        if not all(m.is_ready for m in memberships):
            raise ValueError("Not all players are ready")

        room.status = RoomStatus.ACTIVE
        return await self.room_repo.update(room)
