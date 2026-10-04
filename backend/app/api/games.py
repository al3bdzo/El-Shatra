"""HTTP endpoints for games."""

from typing import Literal

import chess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import messages
from app.deps import game_service

router = APIRouter(prefix="/api/games", tags=["games"])


class CreateGame(BaseModel):
    board_id: str = "sim-1"
    human_color: Literal["white", "black"] = "white"
    level: int = Field(default=1, ge=0, le=20)


@router.post("")
async def create_game(body: CreateGame) -> dict:
    color = chess.WHITE if body.human_color == "white" else chess.BLACK
    game = await game_service.create_game(body.board_id, color, body.level)
    return messages.game_state(game)


@router.get("")
async def list_games() -> list[dict]:
    return [messages.game_state(game) for game in reversed(game_service.all())]


@router.get("/{game_id}")
async def get_game(game_id: str) -> dict:
    game = game_service.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return messages.game_state(game)
