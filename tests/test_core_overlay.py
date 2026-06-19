"""TDD for the engine overlay handling (J4): freeze + open/close routing."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game_engine.core import Game  # noqa: E402
from game_engine.ui.pause_hud import PauseOverlay  # noqa: E402


def keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def game_in_level() -> Game:
    game = Game()
    game.scene = game.registry["level"](game)
    return game


def test_scene_updates_without_overlay() -> None:
    g = game_in_level()
    before = g.scene.remaining_time
    g.step([], 1.0)
    assert g.scene.remaining_time < before


def test_overlay_freezes_scene_update() -> None:
    g = game_in_level()
    g.open_overlay(PauseOverlay(g))
    before = g.scene.remaining_time
    g.step([], 1.0)
    assert g.scene.remaining_time == before


def test_pause_key_opens_overlay() -> None:
    g = game_in_level()
    g.step([keydown(pygame.K_p)], 0.0)
    assert g.overlay is not None


def test_resume_closes_overlay() -> None:
    g = game_in_level()
    g.open_overlay(PauseOverlay(g))
    g.step([keydown(pygame.K_ESCAPE)], 0.0)
    assert g.overlay is None


def test_overlay_return_changes_scene_to_main_menu() -> None:
    g = game_in_level()
    ov = PauseOverlay(g)
    g.open_overlay(ov)
    btn = next(b for b, t in ov.buttons if t == "main_menu")
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                            pos=btn.rect.center)
    g.step([ev], 0.0)
    assert g.overlay is None
    assert g.scene.__class__.__name__ == "MainMenu"
