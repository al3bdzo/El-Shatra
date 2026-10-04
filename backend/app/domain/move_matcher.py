"""Work out which move was played from a new occupancy mask.

The board only knows which squares are occupied, never which piece. We know the
position before the move, so we try every legal move and keep the ones whose
resulting occupancy equals what the board reports.

Captures need one extra rule. After a capture the target square is still occupied
(by the capturing piece), so the final mask looks exactly like "the piece was only
lifted". A capture is therefore accepted only if its target square was seen empty
at some point during the move (`lifted`), i.e. the captured piece was picked up.
"""

from dataclasses import dataclass, field
from enum import Enum

import chess


class MatchKind(str, Enum):
    UNCHANGED = "unchanged"   # board matches the current position
    MOVE = "move"             # exactly one legal move fits
    NONE = "none"             # nothing fits yet (piece in the air, or misplaced)
    AMBIGUOUS = "ambiguous"   # more than one move fits


@dataclass(frozen=True)
class MatchResult:
    kind: MatchKind
    move: chess.Move | None = None
    candidates: tuple[chess.Move, ...] = field(default_factory=tuple)


def match_move(board: chess.Board, new_mask: int, lifted: int = 0) -> MatchResult:
    """Match `new_mask` against the legal moves in `board`.

    `lifted` is a mask of squares that were seen empty since the last move.
    Promotions all give the same mask, so a queen promotion is assumed.
    """
    if new_mask == board.occupied:
        return MatchResult(MatchKind.UNCHANGED)

    found: dict[tuple[int, int], chess.Move] = {}
    for move in board.legal_moves:
        is_plain_capture = board.is_capture(move) and not board.is_en_passant(move)
        if is_plain_capture and not (lifted >> move.to_square) & 1:
            continue
        board.push(move)
        after = board.occupied
        board.pop()
        if after != new_mask:
            continue
        key = (move.from_square, move.to_square)
        if key not in found or move.promotion == chess.QUEEN:
            found[key] = move

    moves = tuple(found.values())
    if not moves:
        return MatchResult(MatchKind.NONE)
    if len(moves) == 1:
        return MatchResult(MatchKind.MOVE, move=moves[0])
    return MatchResult(MatchKind.AMBIGUOUS, candidates=moves)
