"""Integration guard: menu -> level -> pause -> resume via engine.step."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game_engine.core import Game  # noqa: E402


def keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def click_on(button) -> pygame.event.Event:
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                              pos=button.rect.center)


def test_play_then_pause_then_resume() -> None:
    game = Game()
    play_btn = next(b for b, t in game.scene.buttons if t == "level")
    game.step([click_on(play_btn)], 0.016)
    assert game.scene.__class__.__name__ == "PlayingLevel"

    game.step([keydown(pygame.K_p)], 0.016)
    assert game.overlay is not None

    frozen = game.scene.remaining_time
    game.step([], 1.0)
    assert game.scene.remaining_time == frozen

    game.step([keydown(pygame.K_ESCAPE)], 0.016)
    assert game.overlay is None
