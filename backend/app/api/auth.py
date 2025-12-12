from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_player
from app.core import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_db,
    get_logger,
)
from app.models.player import Player
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.player import PlayerCreate, PlayerResponse
from app.services.player_service import PlayerService

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/register",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new player",
)
async def register(payload: PlayerCreate, db: AsyncSession = Depends(get_db)) -> Player:
    service = PlayerService(db)
    try:
        player = await service.create_player(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

    logger.info(
        "Player registered", extra={"player_id": player.id, "username": player.username}
    )
    return player


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT tokens",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {"username": "tank_master", "password": "password123"}
                }
            }
        }
    },
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = PlayerService(db)
    player = await service.authenticate_player(payload.username, payload.password)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    await service.record_login(player)

    access_token = create_access_token({"sub": str(player.id)})
    refresh_token = create_refresh_token({"sub": str(player.id)})

    logger.info(
        "Player logged in",
        extra={
            "player_id": player.id,
            "username": player.username,
            "ip": request.client.host if request.client else None,
        },
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange a refresh token for a new access token",
)
async def refresh_token(payload: RefreshRequest) -> TokenResponse:
    token_payload = decode_token(payload.refresh_token)
    if not token_payload or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    subject = token_payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = create_access_token({"sub": str(subject)})
    refresh_token = create_refresh_token({"sub": str(subject)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout (no-op)")
async def logout() -> None:
    return None


@router.get(
    "/me",
    response_model=PlayerResponse,
    summary="Get the current authenticated player",
)
async def me(current_player: Player = Depends(get_current_player)) -> Player:
    return current_player
