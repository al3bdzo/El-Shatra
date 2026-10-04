"""Golden tests for the move matcher. Add a case for every bug found on the real board."""

import chess

from app.domain.move_matcher import MatchKind, match_move


def sq(name: str) -> int:
    return chess.parse_square(name)


def bit(*names: str) -> int:
    mask = 0
    for name in names:
        mask |= 1 << sq(name)
    return mask


def after(board: chess.Board, uci: str) -> int:
    """Occupancy after playing `uci`, without changing `board`."""
    copy = board.copy()
    copy.push_uci(uci)
    return copy.occupied


def test_unchanged():
    board = chess.Board()
    assert match_move(board, board.occupied).kind == MatchKind.UNCHANGED


def test_quiet_move():
    board = chess.Board()
    result = match_move(board, after(board, "e2e4"))
    assert result.kind == MatchKind.MOVE
    assert result.move == chess.Move.from_uci("e2e4")


def test_piece_in_the_air_is_not_a_move():
    board = chess.Board()
    lifted_e2 = board.occupied & ~bit("e2")
    assert match_move(board, lifted_e2, lifted=bit("e2")).kind == MatchKind.NONE


def test_capture_needs_the_captured_piece_lifted():
    board = chess.Board()
    for uci in ("e2e4", "d7d5"):
        board.push_uci(uci)
    mask = after(board, "e4d5")
    # Only the pawn lifted from e4: looks like a capture, but nothing was taken yet.
    assert match_move(board, mask, lifted=bit("e4")).kind == MatchKind.NONE
    # Black pawn on d5 lifted first, then the white pawn placed there.
    result = match_move(board, mask, lifted=bit("e4", "d5"))
    assert result.kind == MatchKind.MOVE
    assert result.move == chess.Move.from_uci("e4d5")


def test_castling_kingside():
    board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    result = match_move(board, after(board, "e1g1"), lifted=bit("e1", "h1"))
    assert result.kind == MatchKind.MOVE
    assert board.is_castling(result.move)


def test_castling_queenside():
    board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    result = match_move(board, after(board, "e1c1"), lifted=bit("e1", "a1"))
    assert result.move == chess.Move.from_uci("e1c1")


def test_en_passant():
    board = chess.Board("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    result = match_move(board, after(board, "e5d6"), lifted=bit("e5", "d5"))
    assert result.kind == MatchKind.MOVE
    assert board.is_en_passant(result.move)


def test_promotion_defaults_to_queen():
    board = chess.Board("8/4P3/8/8/8/8/k7/4K3 w - - 0 1")
    result = match_move(board, after(board, "e7e8q"))
    assert result.kind == MatchKind.MOVE
    assert result.move.promotion == chess.QUEEN


def test_capture_target_comes_from_which_piece_was_lifted():
    # Knight on e5 can take on d7 or f7; both end with the same occupancy.
    board = chess.Board("4k3/3p1p2/8/4N3/8/8/8/4K3 w - - 0 1")
    mask = after(board, "e5d7")
    result = match_move(board, mask, lifted=bit("e5", "d7"))
    assert result.move == chess.Move.from_uci("e5d7")
    # If both black pawns were picked up and put back, we can't tell.
    assert match_move(board, mask, lifted=bit("e5", "d7", "f7")).kind == MatchKind.AMBIGUOUS
