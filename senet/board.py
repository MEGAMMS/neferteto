"""Board representation and move generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from . import constants as C
from .pieces import PieceState
from .types import PieceRef, PlayerColor


@dataclass(frozen=True)
class Move:
    """Represents a legal action."""

    piece: PieceRef
    start: Optional[int]
    end: Optional[int]
    capture: Optional[PieceRef] = None
    status: str = "normal"  # normal | exit | rebirth
    note: str = ""


def tile_to_grid(tile: int) -> tuple[int, int]:
    """Return (row, col) for rendering."""
    index = tile - 1
    row = index // C.BOARD_COLUMNS
    offset = index % C.BOARD_COLUMNS
    if row % 2 == 0:
        col = offset
    else:
        col = C.BOARD_COLUMNS - 1 - offset
    return row, col


def grid_to_tile(row: int, col: int) -> int:
    """Inverse of :func:`tile_to_grid`."""
    if row % 2 == 0:
        offset = col
    else:
        offset = C.BOARD_COLUMNS - 1 - col
    index = row * C.BOARD_COLUMNS + offset
    return index + 1


class Board:
    """In-memory board with move validation."""

    def __init__(self) -> None:
        self.pieces: Dict[PieceRef, PieceState] = {}
        self.tile_occupants: Dict[int, PieceRef] = {}
        self._init_starting_positions()

    # ------------------------------------------------------------------ setup
    def _init_starting_positions(self) -> None:
        light_idx = 0
        dark_idx = 0
        for i, tile in enumerate(C.STARTING_TILES):
            color = PlayerColor.LIGHT if i % 2 == 0 else PlayerColor.DARK
            if color is PlayerColor.LIGHT:
                ref = PieceRef(color=color, index=light_idx)
                light_idx += 1
            else:
                ref = PieceRef(color=color, index=dark_idx)
                dark_idx += 1
            state = PieceState(ref=ref, position=tile)
            if tile >= C.HOUSE_HAPPINESS:
                state.visited_happiness = True
            self.pieces[ref] = state
            self.tile_occupants[tile] = ref

    # ----------------------------------------------------------------- helpers
    def pieces_for(self, color: PlayerColor) -> Iterable[PieceState]:
        return (state for state in self.pieces.values() if state.ref.color == color)

    def piece_at_tile(self, tile: int) -> Optional[PieceState]:
        ref = self.tile_occupants.get(tile)
        return self.pieces.get(ref) if ref else None

    def move_for_tile(self, color: PlayerColor, tile: int, roll: int) -> Optional[Move]:
        piece = self.piece_at_tile(tile)
        if not piece or piece.ref.color is not color:
            return None
        return self._build_move(piece, roll)

    def finished_count(self, color: PlayerColor) -> int:
        return sum(1 for piece in self.pieces_for(color) if piece.finished)

    # ----------------------------------------------------------------- movement
    def legal_moves(self, color: PlayerColor, roll: int) -> List[Move]:
        moves: List[Move] = []
        for piece in self.pieces_for(color):
            move = self._build_move(piece, roll)
            if move:
                moves.append(move)
        return moves

    def _build_move(self, piece: PieceState, roll: int) -> Optional[Move]:
        if piece.finished or piece.position is None:
            return None
        start = piece.position

        if start == C.HOUSE_THREE_TRUTHS:
            return self._handle_exit_house(piece, roll, required=3, house="House of Three Truths")
        if start == C.HOUSE_RE_ATOUM:
            return self._handle_exit_house(piece, roll, required=2, house="House of Re-Atoum")
        if start == C.HOUSE_HORUS:
            return self._handle_exit_house(piece, roll, required=None, house="House of Horus")

        dest = start + roll

        if not piece.visited_happiness and start < C.HOUSE_HAPPINESS:
            if dest < C.HOUSE_HAPPINESS:
                pass
            elif dest == C.HOUSE_HAPPINESS:
                pass
            else:
                return None

        if dest == C.HOUSE_WATER:
            return self._move_to_rebirth(piece, start, "Fell into the water")

        if dest in (C.HOUSE_THREE_TRUTHS, C.HOUSE_RE_ATOUM, C.HOUSE_HORUS):
            if dest == C.HOUSE_THREE_TRUTHS or dest == C.HOUSE_RE_ATOUM:
                note = "Reached special exit house"
            else:
                note = "Reached House of Horus"
            occupant = self.tile_occupants.get(dest)
            if occupant and occupant.color == piece.ref.color:
                return None
            capture = occupant if occupant else None
            return Move(piece=piece.ref, start=start, end=dest, capture=capture, note=note)

        if dest > C.BOARD_TILES:
            if not piece.visited_happiness:
                return None
            return Move(
                piece=piece.ref,
                start=start,
                end=None,
                status="exit",
                note="Leaves the board",
            )

        occupant = self.tile_occupants.get(dest)
        if occupant and occupant.color == piece.ref.color:
            return None

        if dest == C.HOUSE_HAPPINESS:
            note = "Visited the House of Happiness"
        elif dest == C.HOUSE_REBIRTH:
            note = "Resting in the House of Rebirth"
        else:
            note = ""

        capture = occupant if occupant else None
        return Move(piece=piece.ref, start=start, end=dest, capture=capture, note=note)

    def _handle_exit_house(
        self, piece: PieceState, roll: int, required: Optional[int], house: str
    ) -> Optional[Move]:
        if required is None or roll == required:
            return Move(
                piece=piece.ref,
                start=piece.position,
                end=None,
                status="exit",
                note=f"Exited via {house}",
            )
        return self._move_to_rebirth(piece, piece.position or C.HOUSE_REBIRTH, f"Failed {house}")

    def _move_to_rebirth(self, piece: PieceState, start: int, note: str) -> Move:
        rebirth_tile = self._find_rebirth_tile()
        return Move(
            piece=piece.ref,
            start=start,
            end=rebirth_tile,
            status="rebirth",
            note=note,
        )

    def _find_rebirth_tile(self) -> int:
        for tile in range(C.HOUSE_REBIRTH, 0, -1):
            if tile not in self.tile_occupants:
                return tile
        raise RuntimeError("No available square for rebirth.")

    # --------------------------------------------------------------- mutators
    def apply_move(self, move: Move) -> None:
        piece = self.pieces[move.piece]
        start = move.start
        if start is not None:
            self.tile_occupants.pop(start, None)

        if move.capture:
            captured = self.pieces[move.capture]
            captured.position = start
            captured.finished = False
            self.tile_occupants[start] = move.capture

        if move.status == "exit":
            piece.position = None
            piece.finished = True
            piece.exit_requirement = None
            return

        if move.end is None:
            return

        piece.position = move.end
        if move.status == "rebirth":
            piece.visited_happiness = move.end >= C.HOUSE_HAPPINESS
        elif move.end == C.HOUSE_HAPPINESS:
            piece.visited_happiness = True

        if move.end == C.HOUSE_THREE_TRUTHS:
            piece.exit_requirement = 3
        elif move.end == C.HOUSE_RE_ATOUM:
            piece.exit_requirement = 2
        elif move.end == C.HOUSE_HORUS:
            piece.exit_requirement = None
        else:
            piece.exit_requirement = None

        self.tile_occupants[move.end] = move.piece
