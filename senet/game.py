"""High-level game orchestration."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from .board import Board, Move
from .sticks import StickThrow
from .types import PlayerColor


@dataclass
class TurnContext:
    roll: StickThrow
    moves: List[Move]


class SenetGame:
    """Convenience wrapper tying the board, dice, and turn flow."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self.board = Board()
        self.turn = PlayerColor.LIGHT
        self.rng = random.Random(seed)
        self.last_move: Optional[Move] = None
        self.turn_count = 0

    # ----------------------------------------------------------------- rolling
    def roll(self) -> StickThrow:
        throw = StickThrow.random(self.rng)
        return throw

    # ------------------------------------------------------------ move helpers
    def legal_moves(self, roll: StickThrow) -> List[Move]:
        return self.board.legal_moves(self.turn, roll.value)

    def apply_move(self, move: Move) -> None:
        self.board.apply_move(move)
        self.last_move = move
        self.turn = self.turn.opponent
        self.turn_count += 1

    def skip_turn(self) -> None:
        self.last_move = None
        self.turn = self.turn.opponent
        self.turn_count += 1

    def winner(self) -> Optional[PlayerColor]:
        for color in PlayerColor:
            if self.board.finished_count(color) == 7:
                return color
        return None

    # --------------------------------------------------------- simple computer
    def choose_ai_move(self, roll: StickThrow) -> Optional[Move]:
        moves = self.legal_moves(roll)
        if not moves:
            return None
        moves.sort(key=self._score_move, reverse=True)
        return moves[0]

    def _score_move(self, move: Move) -> float:
        if move.status == "exit":
            return 100.0
        if move.status == "rebirth":
            return -20.0
        score = float(move.end or 0)
        if move.capture:
            score += 2.0
        return score
