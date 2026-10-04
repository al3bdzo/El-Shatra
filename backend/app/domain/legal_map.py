"""Legal destinations per square, so the board can light them the moment a piece is lifted."""

import chess


def legal_map(board: chess.Board) -> dict[int, int]:
    """Return {from_square: mask of legal destination squares}."""
    result: dict[int, int] = {}
    for move in board.legal_moves:
        result[move.from_square] = result.get(move.from_square, 0) | (1 << move.to_square)
    return result
