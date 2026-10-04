"""End to end through the API: create a game, play a move from a fake board, get the engine reply."""

import time

import chess
from fastapi.testclient import TestClient

from app.adapters.engine import RandomPlayer
from app.config import settings
from app.deps import game_service
from app.domain.occupancy import to_hex
from app.main import app

game_service.player = RandomPlayer()   # tests never need Stockfish
client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_unknown_game_is_404():
    assert client.get("/api/games/nope").status_code == 404


def test_bad_token_is_rejected():
    with client.websocket_connect("/ws/board") as ws:
        ws.send_json({"type": "hello", "board_id": "x", "token": "wrong"})
        assert ws.receive_json()["type"] == "error"


def test_one_move_end_to_end():
    with client.websocket_connect("/ws/board") as board:
        board.send_json({"type": "hello", "board_id": "test-board", "token": settings.board_token})
        assert board.receive_json() == {"type": "welcome", "game_id": None}

        game = client.post("/api/games", json={"board_id": "test-board", "human_color": "white"}).json()
        assert board.receive_json() == {"type": "welcome", "game_id": game["game_id"]}
        position = board.receive_json()
        assert position["type"] == "position" and position["my_turn"] is True
        assert board.receive_json()["type"] == "leds"

        # Play e2e4 on the "board".
        start = chess.Board()
        board.send_json({"type": "occupancy", "seq": 1, "mask": to_hex(start.occupied & ~(1 << chess.E2))})
        start.push_uci("e2e4")
        board.send_json({"type": "occupancy", "seq": 2, "mask": to_hex(start.occupied)})

        # Wait for the engine's reply.
        state = {}
        for _ in range(50):
            state = client.get(f"/api/games/{game['game_id']}").json()
            if len(state["moves"]) == 2:
                break
            time.sleep(0.05)
        assert state["moves"][0] == "e2e4"
        assert len(state["moves"]) == 2
        assert state["awaiting_physical"] is True
