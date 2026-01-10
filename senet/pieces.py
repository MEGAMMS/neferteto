"""Piece-level data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .types import PieceRef


@dataclass
class PieceState:
    """Tracks runtime information about a single piece."""

    ref: PieceRef
    position: Optional[int]
    finished: bool = False
    visited_happiness: bool = False
    exit_requirement: Optional[int] = None  # 2 or 3 mean exact roll, -1 means any roll

    def clone(self) -> "PieceState":
        return PieceState(
            ref=self.ref,
            position=self.position,
            finished=self.finished,
            visited_happiness=self.visited_happiness,
            exit_requirement=self.exit_requirement,
        )
