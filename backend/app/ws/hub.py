"""Keeps track of open WebSockets and sends every change to whoever needs it."""

from collections import defaultdict

from fastapi import WebSocket

from app import messages
from app.services.game_service import Game


class Hub:
    def __init__(self) -> None:
        self.viewers: dict[str, set[WebSocket]] = defaultdict(set)   # game_id -> browsers
        self.boards: dict[str, WebSocket] = {}                       # board_id -> board
        self._board_game: dict[str, str] = {}                        # board_id -> game it was told about

    async def publish(self, game: Game) -> None:
        state = messages.game_state(game)
        for ws in list(self.viewers[game.id]):
            try:
                await ws.send_json(state)
            except Exception:
                self.viewers[game.id].discard(ws)

        board_ws = self.boards.get(game.board_id)
        if board_ws is None:
            return
        try:
            if self._board_game.get(game.board_id) != game.id:
                await board_ws.send_json(messages.welcome(game))
                self._board_game[game.board_id] = game.id
            await board_ws.send_json(messages.position(game))
            await board_ws.send_json(messages.leds(game))
        except Exception:
            self.remove_board(game.board_id, board_ws)

    def add_board(self, board_id: str, ws: WebSocket) -> None:
        self.boards[board_id] = ws
        self._board_game.pop(board_id, None)

    def remove_board(self, board_id: str, ws: WebSocket) -> None:
        if self.boards.get(board_id) is ws:
            del self.boards[board_id]
            self._board_game.pop(board_id, None)
