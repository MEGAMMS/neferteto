"""Minimal pygame visualisation for the Senet model."""

from __future__ import annotations

import io
from pathlib import Path
from textwrap import wrap
from typing import Dict, Iterable, Optional, Tuple

import pygame
from pygame import gfxdraw
from cairosvg import svg2png

from . import constants as C
from .board import Move, grid_to_tile, tile_to_grid
from .game import SenetGame
from .sticks import StickThrow
from .types import PieceRef, PlayerColor


def _hex(color: str) -> Tuple[int, int, int]:
    color = color.lstrip("#")
    # type: ignore[misc]
    return tuple(int(color[i: i + 2], 16) for i in (0, 2, 4))


PALETTE = {
    "background": _hex("#808080"),
    "board_surface": _hex("#6d6d6d"),
    "tile_dark": _hex("#deb887"),
    "tile_light": _hex("#f5f5dc"),
    "piece_light": _hex("#fffafa"),
    "piece_dark": _hex("#708090"),
    "highlight": _hex("#99fa98"),
    "frame": _hex("#000000"),
    "stick_dark": _hex("#bc8f8f"),
    "stick_light": _hex("#fffaf0"),
    "panel_bg": _hex("#deb887"),
}

TILE_SIZE = 110
TILE_GAP = 20
BOARD_STEP = TILE_SIZE + TILE_GAP
PADDING = 40
PANEL_HEIGHT = 210
PANEL_GAP = 16
BOARD_WIDTH = C.BOARD_COLUMNS * BOARD_STEP - TILE_GAP
BOARD_HEIGHT = C.BOARD_ROWS * BOARD_STEP - TILE_GAP
BOARD_OFFSET_X = PADDING
BOARD_OFFSET_Y = PADDING + PANEL_HEIGHT + PANEL_GAP
WINDOW_WIDTH = BOARD_WIDTH + PADDING * 2
WINDOW_HEIGHT = BOARD_OFFSET_Y + BOARD_HEIGHT + PADDING
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
BOARD_BORDER_RADIUS = 28
TILE_BORDER_RADIUS = 18
TEXT_PADDING = 12
LINE_SPACING = 6
MESSAGE_WRAP = 60

SPECIAL_ICONS = {
    C.HOUSE_REBIRTH: "rebirth.svg",
    C.HOUSE_HAPPINESS: "happy.svg",
    C.HOUSE_WATER: "water.svg",
    C.HOUSE_THREE_TRUTHS: "three.svg",
    C.HOUSE_RE_ATOUM: "two.svg",
    C.HOUSE_HORUS: "horus.svg",
}

PROBABILITY_LOOKUP = {
    throw.value: throw.probability for throw in StickThrow.distribution()}


class SenetApp:
    """Encapsulates pygame drawing and input handling."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Senet Prototype")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.big_font = pygame.font.SysFont("arial", 28, bold=True)
        self.game = SenetGame()
        self.current_roll: StickThrow = self.game.roll()
        self.current_moves: Dict[PieceRef, Move] = {}
        self.message = "Welcome to Senet"
        self.icons = self._load_icons()
        self.running = True
        self._prepare_turn()

    # ----------------------------------------------------------------- helpers (geometry / drawing)
    def _tile_rect(self, row: int, col: int) -> pygame.Rect:
        return pygame.Rect(
            BOARD_OFFSET_X + col * BOARD_STEP,
            BOARD_OFFSET_Y + row * BOARD_STEP,
            TILE_SIZE,
            TILE_SIZE,
        )

    @staticmethod
    def _draw_disc(surface: pygame.Surface, center: Tuple[int, int], radius: int, fill: Tuple[int, int, int], border: Tuple[int, int, int]) -> None:
        if radius <= 0:
            return
        gfxdraw.filled_circle(surface, center[0], center[1], radius, border)
        gfxdraw.aacircle(surface, center[0], center[1], radius, border)
        inner_radius = max(radius - 3, 2)
        gfxdraw.filled_circle(surface, center[0], center[1], inner_radius, fill)
        gfxdraw.aacircle(surface, center[0], center[1], inner_radius, fill)

    @staticmethod
    def _rounded_rect(surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], radius: int, width: int = 0) -> None:
        upscale = 2
        temp = pygame.Surface((rect.width * upscale, rect.height * upscale), pygame.SRCALPHA)
        scaled_radius = max(radius * upscale, 1)
        scaled_width = width * upscale
        pygame.draw.rect(
            temp,
            color,
            pygame.Rect(0, 0, rect.width * upscale, rect.height * upscale),
            scaled_width,
            border_radius=scaled_radius,
        )
        smooth = pygame.transform.smoothscale(temp, (rect.width, rect.height))
        surface.blit(smooth, rect.topleft)

    @staticmethod
    def _wrap_text(text: str, limit: int) -> Iterable[str]:
        return wrap(text, limit) if text else []

    def _blit_lines(self, font: pygame.font.Font, lines: Iterable[str], x: int, y: int) -> int:
        for line in lines:
            surface = font.render(line, True, PALETTE["frame"])
            self.screen.blit(surface, (x, y))
            y += surface.get_height() + LINE_SPACING
        return y

    # ----------------------------------------------------------------- assets
    def _load_icons(self) -> Dict[int, pygame.Surface]:
        assets: Dict[int, pygame.Surface] = {}
        base = Path(__file__).resolve().parent.parent / "assets" / "images"
        icon_size = TILE_SIZE - 8
        for tile, filename in SPECIAL_ICONS.items():
            path = base / filename
            if not path.exists():
                continue
            png_bytes = svg2png(url=str(path), output_width=icon_size, output_height=icon_size)
            image = pygame.image.load(io.BytesIO(png_bytes)).convert_alpha()
            scaled = pygame.transform.smoothscale(image, (icon_size, icon_size))
            assets[tile] = scaled
        return assets

    # --------------------------------------------------------------- main loop
    def run(self) -> None:
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

    # --------------------------------------------------------------- game flow
    def _prepare_turn(self) -> None:
        for _ in range(10):
            self.current_roll = self.game.roll()
            moves = self.game.legal_moves(self.current_roll)
            self.current_moves = {move.piece: move for move in moves}
            if moves:
                self.message = (
                    f"{self.game.turn.name.title()} rolled {self.current_roll.value} "
                    f"(p={PROBABILITY_LOOKUP.get(self.current_roll.value, 0):.2f}). "
                    "Select one of the highlighted pieces."
                )
                return
            self.message = (
                f"{self.game.turn.name.title()} rolled {self.current_roll.value} "
                "but has no moves."
            )
            self.game.skip_turn()
        self.message = "No moves available for either player."

    def _update(self) -> None:
        winner = self.game.winner()
        if winner:
            self.message = f"{winner.name.title()} wins!"
            self.running = False

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_click(self, pos: Tuple[int, int]) -> None:
        tile = self._tile_from_position(pos)
        if tile is None:
            return
        piece = self.game.board.piece_at_tile(tile)
        if not piece or piece.ref.color is not self.game.turn:
            return
        move = self.current_moves.get(piece.ref)
        if not move:
            return
        self.game.apply_move(move)
        start = move.start if move.start is not None else "off-board"
        dest = "off-board" if move.status == "exit" else move.end
        self.message = f"{piece.ref.color.name.title()} moved {start}→{dest}."
        self._prepare_turn()

    # ------------------------------------------------------------------- draw
    def _draw(self) -> None:
        self.screen.fill(PALETTE["background"])
        self._draw_board()
        self._draw_side_panel()

    def _draw_board(self) -> None:
        board_rect = pygame.Rect(
            BOARD_OFFSET_X - TILE_GAP // 2,
            BOARD_OFFSET_Y - TILE_GAP // 2,
            BOARD_WIDTH + TILE_GAP,
            BOARD_HEIGHT + TILE_GAP,
        )
        self._rounded_rect(self.screen, board_rect, PALETTE["board_surface"], BOARD_BORDER_RADIUS)
        movable_refs = set(self.current_moves.keys())

        for tile in range(1, C.BOARD_TILES + 1):
            row, col = tile_to_grid(tile)
            rect = self._tile_rect(row, col)
            # alternating checkerboard regardless of special icon
            base_color = (
                PALETTE["tile_light"] if (
                    row + col) % 2 == 0 else PALETTE["tile_dark"]
            )
            self._rounded_rect(self.screen, rect, base_color, TILE_BORDER_RADIUS)
            self._rounded_rect(self.screen, rect, PALETTE["frame"], TILE_BORDER_RADIUS, width=2)
            # Special icon overlay
            icon = self.icons.get(tile)
            if icon:
                icon_rect = icon.get_rect(center=rect.center)
                self.screen.blit(icon, icon_rect)

        for piece in self.game.board.pieces.values():
            if piece.finished or piece.position is None:
                continue
            row, col = tile_to_grid(piece.position)
            rect = self._tile_rect(row, col)
            center_int = (rect.centerx, rect.centery)
            radius = TILE_SIZE // 2 - 20
            color = (
                PALETTE["piece_light"] if piece.ref.color is PlayerColor.LIGHT else PALETTE["piece_dark"]
            )
            self._draw_disc(self.screen, center_int, radius, color, PALETTE["frame"])

        # highlight movable pieces for the current player
        for ref in movable_refs:
            piece_state = self.game.board.pieces.get(ref)
            if not piece_state or piece_state.position is None:
                continue
            if piece_state.ref.color is not self.game.turn:
                continue
            row, col = tile_to_grid(piece_state.position)
            rect = self._tile_rect(row, col)
            self._rounded_rect(self.screen, rect, PALETTE["highlight"], TILE_BORDER_RADIUS, width=4)

    def _draw_side_panel(self) -> None:
        panel_rect = pygame.Rect(
            PADDING,
            PADDING,
            BOARD_WIDTH,
            PANEL_HEIGHT,
        )
        self._rounded_rect(self.screen, panel_rect, PALETTE["panel_bg"], radius=12)
        text_x = panel_rect.x + TEXT_PADDING
        text_y = panel_rect.y + TEXT_PADDING

        text_y = self._blit_lines(self.big_font, ("Senet",), text_x, text_y)
        text_y = self._blit_lines(self.font, (f"Turn: {self.game.turn.name.title()}",), text_x, text_y)
        text_y = self._blit_lines(self.small_font, self._wrap_text(self.message, MESSAGE_WRAP), text_x, text_y)
        text_y = self._blit_lines(
            self.font,
            (
                f"Roll: {self.current_roll.value} steps",
                f"Prob: {PROBABILITY_LOOKUP.get(self.current_roll.value, 0.0):.2%}",
            ),
            text_x,
            text_y,
        )

        # Toss sticks visualization anchored to the right side
        stick_height = 70
        stick_width = 26
        stick_gap = 8
        total_width = 4 * stick_width + 3 * stick_gap
        stick_area_top = panel_rect.y + 20
        start_x = panel_rect.right - total_width - 20
        faces = self._faces_from_roll(self.current_roll.value)
        for i, face in enumerate(faces):
            stick_rect = pygame.Rect(
                start_x + i * (stick_width + stick_gap),
                stick_area_top,
                stick_width,
                stick_height,
            )
            face_color = PALETTE["stick_light"] if face == 0 else PALETTE["stick_dark"]
            self._rounded_rect(self.screen, stick_rect, face_color, radius=8)
            self._rounded_rect(self.screen, stick_rect, PALETTE["frame"], radius=8, width=2)

        finish_box = pygame.Rect(
            panel_rect.x + panel_rect.width // 2 - 110,
            panel_rect.bottom - 80,
            220,
            60,
        )
        self._rounded_rect(self.screen, finish_box, PALETTE["tile_light"], radius=8)
        self._rounded_rect(self.screen, finish_box, PALETTE["frame"], radius=8, width=2)
        finish_text_x = finish_box.x + TEXT_PADDING
        finish_text_y = finish_box.y + TEXT_PADDING
        finish_text_y = self._blit_lines(self.font, ("Finished:",), finish_text_x, finish_text_y)
        self._blit_lines(
            self.small_font,
            (
                f"Light: {self.game.board.finished_count(PlayerColor.LIGHT)}",
                f"Dark: {self.game.board.finished_count(PlayerColor.DARK)}",
            ),
            finish_text_x,
            finish_text_y,
        )

    # ----------------------------------------------------------------- helpers
    def _tile_from_position(self, pos: Tuple[int, int]) -> Optional[int]:
        origin_x = BOARD_OFFSET_X
        origin_y = BOARD_OFFSET_Y
        x, y = pos
        if x < origin_x or y < origin_y:
            return None
        rel_x = x - origin_x
        rel_y = y - origin_y
        col = rel_x // BOARD_STEP
        row = rel_y // BOARD_STEP
        if col < 0 or row < 0 or col >= C.BOARD_COLUMNS or row >= C.BOARD_ROWS:
            return None
        # Ignore clicks that fall inside the gap between tiles.
        if rel_x % BOARD_STEP > TILE_SIZE or rel_y % BOARD_STEP > TILE_SIZE:
            return None
        tile = grid_to_tile(int(row), int(col))
        return tile

    def _faces_from_roll(self, value: int) -> Tuple[int, int, int, int]:
        """Return a canonical arrangement of stick faces for a given roll value."""
        if value == 5:
            return (0, 0, 0, 0)
        if value == 4:
            return (1, 1, 1, 1)
        faces = [0, 0, 0, 0]
        for i in range(value):
            faces[i] = 1
        return tuple(faces)


def run() -> None:
    app = SenetApp()
    app.run()
