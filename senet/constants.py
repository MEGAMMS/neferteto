"""Constants describing the Senet board."""

from __future__ import annotations

BOARD_TILES = 30
BOARD_COLUMNS = 10
BOARD_ROWS = 3
PIECES_PER_PLAYER = 7

HOUSE_REBIRTH = 15
HOUSE_HAPPINESS = 26
HOUSE_WATER = 27
HOUSE_THREE_TRUTHS = 28
HOUSE_RE_ATOUM = 29
HOUSE_HORUS = 30

SPECIAL_HOUSES = {
    HOUSE_REBIRTH: "rebirth",
    HOUSE_HAPPINESS: "happiness",
    HOUSE_WATER: "water",
    HOUSE_THREE_TRUTHS: "three-truths",
    HOUSE_RE_ATOUM: "re-atoum",
    HOUSE_HORUS: "horus",
}

# The first fourteen tiles are populated at startup, alternating colors.
STARTING_TILES = list(range(1, 15))
