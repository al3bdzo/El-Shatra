"""Builds the JSON messages sent to boards and browsers (see docs/protocol.md)."""

import chess

from app.domain.legal_map import legal_map
from app.domain.occupancy import to_hex
from app.services.game_service import Game


def _color(color: chess.Color) -> str:
    return "white" if color == chess.WHITE else "black"


# ---- to browsers ----------------------------------------------------------------

def game_state(game: Game) -> dict:
    return {
        "type": "game_state",
        "game_id": game.id,
        "board_id": game.board_id,
        "fen": game.board.fen(),
        "moves": [move.uci() for move in game.board.move_stack],
        "last_move": game.last_move.uci() if game.last_move else None,
        "turn": _color(game.board.turn),
        "human_color": _color(game.human_color),
        "level": game.level,
        "status": game.status,
        "result": game.board.result() if game.is_over else None,
        "awaiting_physical": game.awaiting_physical,
        "sync_squares": [chess.square_name(sq) for sq in chess.SquareSet(game.unexpected)],
    }


# ---- to boards ------------------------------------------------------------------

def welcome(game: Game | None) -> dict:
    return {"type": "welcome", "game_id": game.id if game else None}


def position(game: Game) -> dict:
    legal = legal_map(game.board) if game.humans_turn else {}
    return {
        "type": "position",
        "expected_mask": to_hex(game.board.occupied),
        "legal_map": {str(square): to_hex(mask) for square, mask in legal.items()},
        "my_turn": game.humans_turn,
    }


def leds(game: Game) -> dict:
    """What the board should light right now. Colours follow the architecture doc."""
    frame: list[dict] = []
    if game.awaiting_physical and game.last_move:
        frame.append({"sq": game.last_move.from_square, "color": "blue", "effect": "solid"})
        frame.append({"sq": game.last_move.to_square, "color": "blue", "effect": "blink"})
    for square in chess.SquareSet(game.unexpected):
        frame.append({"sq": square, "color": "red", "effect": "solid"})
    if game.board.is_check() and not game.awaiting_physical:
        king = game.board.king(game.board.turn)
        if king is not None:
            frame.append({"sq": king, "color": "yellow", "effect": "solid"})
    if game.is_over:
        frame = [{"sq": sq, "color": "white", "effect": "pulse"} for sq in chess.SquareSet(game.board.occupied)]
    return {"type": "leds", "frame": frame}


def error(code: str, message: str) -> dict:
    return {"type": "error", "code": code, "message": message}
