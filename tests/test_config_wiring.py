"""TDD for sourcing PlayingLevel constants from config (J8 / M2)."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402,F401

from game_engine.core import Game  # noqa: E402
from game_engine.config import get_gamemode_cfg  # noqa: E402


def level():
    game = Game()
    return game.registry["level"](game)


def test_constants_come_from_config() -> None:
    pl = level()
    cfg = get_gamemode_cfg()
    assert pl.lives == cfg["lives"]
    assert pl.time_limit == cfg["level_max_time"]
    assert pl.frightened_duration == cfg["frightened_duration"]
    assert pl.points_gum == cfg["points_per_gum"]
    assert pl.points_power == cfg["points_per_power_gum"]
    assert pl.points_ghost == cfg["points_1st_ghost"]
