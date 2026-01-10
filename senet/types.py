"""Core enums and lightweight identifiers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PlayerColor(str, Enum):
    """Two Senet sides."""

    LIGHT = "light"
    DARK = "dark"

    @property
    def opponent(self) -> "PlayerColor":
        return PlayerColor.DARK if self is PlayerColor.LIGHT else PlayerColor.LIGHT


@dataclass(frozen=True)
class PieceRef:
    """Immutable identifier for a specific piece."""

    color: PlayerColor
    index: int

    def label(self) -> str:
        prefix = "L" if self.color is PlayerColor.LIGHT else "D"
        return f"{prefix}{self.index + 1}"
