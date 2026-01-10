"""Stick-throw probabilities and helpers."""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


def _roll_value(faces: Iterable[int]) -> int:
    """Sum faces (1 for dark, 0 for light) with the special-case 0->5 rule."""
    total = sum(faces)
    return total if total > 0 else 5


def _all_rolls() -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for faces in itertools.product((0, 1), repeat=4):
        value = _roll_value(faces)
        counts[value] = counts.get(value, 0) + 1
    return counts


_ROLL_COUNTS = _all_rolls()
_TOTAL_OUTCOMES = sum(_ROLL_COUNTS.values())


@dataclass(frozen=True)
class StickThrow:
    """Represents a throw outcome."""

    value: int
    probability: float

    @staticmethod
    def distribution() -> List["StickThrow"]:
        return [
            StickThrow(value=k, probability=count / _TOTAL_OUTCOMES)
            for k, count in sorted(_ROLL_COUNTS.items())
        ]

    @staticmethod
    def random(rng: Optional[random.Random] = None) -> "StickThrow":
        rng = rng or random
        faces = [rng.randint(0, 1) for _ in range(4)]
        return StickThrow(value=_roll_value(faces), probability=0.0)
