"""Default configuration ; single source of truth for fallback values.

Imported by config.py as _FALLBACK_CONFIG; nothing else should import this.
All values here are the game's built-in defaults, used when config.json is
absent, corrupted, or missing a key.
"""

from typing import Any


class _Schema:
    """Namespace base: exposes class attributes as a lowercase-keyed dict."""

    @classmethod
    def as_dict(cls) -> dict[Any, Any]:
        return {k.lower(): v for k, v in vars(cls).items()
                if not k.startswith("_") and not callable(v)}


# -- Structural schemas -------------------------------------------------------

class Window(_Schema):
    TITLE = "Pac-Man"
    WIDTH = 800
    HEIGHT = 600
    FPS = 60


class Levels(_Schema):
    SEED = 42
    WIDTH = 20
    HEIGHT = 20
    DIMS = [
        [20, 20],   # Level 01
        [21, 21],   # Level 02
        [22, 22],   # Level 03
        [23, 23],   # Level 04
        [24, 24],   # Level 05
        [25, 25],   # Level 06
        [26, 26],   # Level 07
        [27, 27],   # Level 08
        [28, 28],   # Level 09
        [29, 29],   # Level 10
    ]


class App(_Schema):
    VERSION = "1.0.0"
    DEFAULT_PLAYER_NAME = "PLAYER"


class Colors(_Schema):
    BG = [10,  10,  30]
    BG_INSTRUCTIONS = [30,  10,  10]
    BG_GAME = [0,   0,   0]
    IRONMAN_BG = [50,  0,   0]
    TITLE = [255, 215, 0]
    TEXT = [255, 255, 255]
    HINT = [150, 150, 150]
    HEADER = [255, 203, 71]
    WALL = [33,  33,  255]
    PACMAN = [255, 255, 0]
    PAC_GUM = [255, 255, 255]
    GHOST_FRIGHTENED = [50,  150, 255]
    WIN = [255, 215, 0]
    LOSE = [220, 60,  60]
    BUTTON_IDLE = [40,  40,  40]
    BUTTON_HOVER = [70,  70,  90]
    BUTTON_BORDER = [255, 215, 0]


# -- Game mode schemas --------------------------------------------------------

class Common(_Schema):
    SPEED_MULTIPLIER = 1.0
    GHOST_SPEED = 3.0
    GHOST_FRIGHTENED_SPEED = 2.0
    GHOST_DEAD_SPEED_MULT = 2.0
    PACMAN_SPEED = 4.0
    COLLISION_RADIUS_RATIO = 0.7
    POINTS_PER_GUM = 10
    POINTS_PER_POWER_GUM = 50
    POINTS_PER_GHOST = 200


class Original(_Schema):
    LIVES                = 3
    LEVEL_MAX_TIME       = 300
    FRIGHTENED_DURATION  = 6.0
    SCATTER_DURATIONS    = [7, 7, 5, 5]
    CHASE_DURATIONS      = [20, 20, 20, 999]


class Ironman(_Schema):
    SPEED_MULTIPLIER     = 1.3
    LIVES                = 1
    LEVEL_MAX_TIME       = 180
    FRIGHTENED_DURATION  = 5.0
    SCATTER_DURATIONS    = [7, 7, 5, 5]
    CHASE_DURATIONS      = [30, 30, 30, 999]


class Scores(_Schema):
    ORIGINAL: list = []
    IRONMAN:  list = []


# -- Assembled fallback dict (consumed by config.py) --------------------------

FALLBACK_CONFIG: dict[Any, Any] = {
    "window": Window.as_dict(),
    "levels": Levels.as_dict(),
    "app":    App.as_dict(),
    "game": {
        "common":   Common.as_dict(),
        "original": Original.as_dict(),
        "ironman":  Ironman.as_dict(),
    },
    "ui": {
        "colors": Colors.as_dict(),
    },
    "scores": {
        "original": Scores.ORIGINAL,
        "ironman":  Scores.IRONMAN,
    },
}
