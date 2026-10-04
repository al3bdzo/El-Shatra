"""Engines that choose moves. The game service only knows the `MovePlayer` interface,
so a new engine (or the team's own model) is a new class with `choose_move`."""

import asyncio
import random
import shutil
from typing import Protocol

import chess
import chess.engine


class MovePlayer(Protocol):
    async def choose_move(self, board: chess.Board, level: int) -> chess.Move: ...


class RandomPlayer:
    """Plays a random legal move. Used when Stockfish isn't installed."""

    async def choose_move(self, board: chess.Board, level: int) -> chess.Move:
        return random.choice(list(board.legal_moves))


class StockfishPlayer:
    """Stockfish via python-chess. `level` maps to Stockfish's Skill Level (0-20)."""

    def __init__(self, path: str, move_time: float) -> None:
        self.path = path
        self.move_time = move_time

    async def choose_move(self, board: chess.Board, level: int) -> chess.Move:
        return await asyncio.to_thread(self._choose, board.copy(), level)

    def _choose(self, board: chess.Board, level: int) -> chess.Move:
        with chess.engine.SimpleEngine.popen_uci(self.path) as engine:
            engine.configure({"Skill Level": max(0, min(20, level))})
            result = engine.play(board, chess.engine.Limit(time=self.move_time))
            return result.move


def make_player(stockfish_path: str, move_time: float) -> MovePlayer:
    path = stockfish_path or shutil.which("stockfish")
    if path:
        return StockfishPlayer(path, move_time)
    return RandomPlayer()
