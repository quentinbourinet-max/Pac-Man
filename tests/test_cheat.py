"""TDD for cheat mode (J9 / O6 / M40): F1 invincibility, F2 skip level."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game_engine.core import Game  # noqa: E402


def keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def level():
    game = Game()
    return game.registry["level"](game)


def force_ghost_on_pacman(pl) -> None:
    pl.ghosts[0].coord = list(pl.pacman.coord)
    pl.ghosts[0].state = "normal"
    pl.ghosts[0].dir = "NONE"
    pl.pacman.dir = "NONE"


def test_f1_toggles_invincibility() -> None:
    pl = level()
    assert pl.invincible is False
    pl.handle_events([keydown(pygame.K_F1)])
    assert pl.invincible is True


def test_invincible_survives_normal_ghost() -> None:
    pl = level()
    pl.invincible = True
    pl.lives = 3
    force_ghost_on_pacman(pl)
    pl.update(0.0)
    assert pl.lives == 3
    assert pl.go_to_scene is None


def test_normal_ghost_costs_a_life_without_cheat() -> None:
    pl = level()
    pl.lives = 3
    force_ghost_on_pacman(pl)
    pl.update(0.0)
    assert pl.lives == 2


def test_f2_skips_to_next_level() -> None:
    pl = level()
    pl.level_id = 1
    pl.handle_events([keydown(pygame.K_F2)])
    pl.update(1.0)
    assert pl.level_id == 2
