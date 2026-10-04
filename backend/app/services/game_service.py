"""Games and their rules of play. Games live in memory for now.

v1 has one kind of game: a human on a board (real or simulated) against the engine.
Seats, online play and storage in a database are features to add on top of this.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Protocol

import chess

from app.adapters.engine import MovePlayer
from app.domain.move_matcher import MatchKind, match_move


@dataclass
class Game:
    id: str
    board_id: str
    human_color: chess.Color
    level: int
    board: chess.Board = field(default_factory=chess.Board)
    last_move: chess.Move | None = None
    # Squares seen empty since the last move (needed to recognise captures).
    lifted: int = 0
    # Occupied squares that should be empty: shown red until fixed.
    unexpected: int = 0
    # The engine has moved; waiting for the player to make that move on the board.
    awaiting_physical: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    @property
    def is_over(self) -> bool:
        return self.board.is_game_over()

    @property
    def status(self) -> str:
        if self.is_over:
            return "finished"
        if self.unexpected:
            return "syncing"
        return "active"

    @property
    def humans_turn(self) -> bool:
        return self.board.turn == self.human_color and not self.awaiting_physical and not self.is_over


class Notifier(Protocol):
    """Whoever needs to hear about changes (the WebSocket hub)."""

    async def publish(self, game: Game) -> None: ...


class GameService:
    def __init__(self, player: MovePlayer, notifier: Notifier) -> None:
        self.player = player
        self.notifier = notifier
        self.games: dict[str, Game] = {}
        self._tasks: set[asyncio.Task] = set()   # keeps running engine turns alive

    def _start_engine_turn(self, game: Game) -> None:
        task = asyncio.create_task(self._engine_turn(game))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    # ---- queries -------------------------------------------------------------

    def get(self, game_id: str) -> Game | None:
        return self.games.get(game_id)

    def all(self) -> list[Game]:
        return list(self.games.values())

    def active_for_board(self, board_id: str) -> Game | None:
        """The most recent unfinished game played on this board."""
        for game in reversed(list(self.games.values())):
            if game.board_id == board_id and not game.is_over:
                return game
        return None

    # ---- commands ------------------------------------------------------------

    async def create_game(self, board_id: str, human_color: chess.Color, level: int) -> Game:
        game = Game(id=uuid.uuid4().hex[:8], board_id=board_id, human_color=human_color, level=level)
        self.games[game.id] = game
        await self.notifier.publish(game)
        if game.board.turn != human_color:
            self._start_engine_turn(game)
        return game

    async def on_occupancy(self, game: Game, mask: int) -> None:
        """Called every time the board reports a new stable occupancy."""
        async with game.lock:
            if game.is_over:
                return
            expected = game.board.occupied
            game.unexpected = mask & ~expected

            if game.awaiting_physical:
                # The player is reproducing the engine's move on the board.
                if mask == expected:
                    game.awaiting_physical = False
                    game.lifted = 0
            elif game.board.turn == game.human_color:
                game.lifted |= expected & ~mask
                result = match_move(game.board, mask, game.lifted)
                if result.kind == MatchKind.UNCHANGED:
                    game.lifted = 0
                elif result.kind == MatchKind.MOVE:
                    game.board.push(result.move)
                    game.last_move = result.move
                    game.lifted = 0
                    game.unexpected = 0
                    if not game.is_over:
                        self._start_engine_turn(game)
        await self.notifier.publish(game)

    async def _engine_turn(self, game: Game) -> None:
        move = await self.player.choose_move(game.board.copy(), game.level)
        async with game.lock:
            game.board.push(move)
            game.last_move = move
            game.lifted = 0
            game.awaiting_physical = True
        await self.notifier.publish(game)
