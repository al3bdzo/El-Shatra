"""Occupancy masks: bit i set = square i occupied (0 = a1, 7 = h1, 56 = a8, 63 = h8).

This is the same numbering python-chess uses, so `board.occupied` is already a mask.
On the wire a mask is 16 hex characters.
"""


def to_hex(mask: int) -> str:
    return f"{mask:016x}"


def from_hex(text: str) -> int:
    return int(text, 16)
