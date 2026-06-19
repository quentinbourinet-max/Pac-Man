"""TDD for the PauseOverlay (J4 / M45 / M51)."""

import pygame

from game_engine.definitions import CLOSE
from game_engine.ui.pause_hud import PauseOverlay


class FakeGame:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600


def make_overlay() -> PauseOverlay:
    pygame.font.init()
    return PauseOverlay(FakeGame())


def keydown(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def click(ov: PauseOverlay, target: str) -> str | None:
    btn = next(b for b, t in ov.buttons if t == target)
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                            pos=btn.rect.center)
    return ov.handle_events([ev])


def test_escape_resumes() -> None:
    ov = make_overlay()
    assert ov.handle_events([keydown(pygame.K_ESCAPE)]) == CLOSE


def test_p_resumes() -> None:
    ov = make_overlay()
    assert ov.handle_events([keydown(pygame.K_p)]) == CLOSE


def test_resume_button_resumes() -> None:
    assert click(make_overlay(), CLOSE) == CLOSE


def test_main_menu_button_leaves() -> None:
    assert click(make_overlay(), "main_menu") == "main_menu"


def test_render_draws_onto_surface() -> None:
    ov = make_overlay()
    surface = pygame.Surface((ov.game.width, ov.game.height))
    surface.fill((1, 2, 3))
    ov.render(surface)
    changed = any(
        surface.get_at((x, y))[:3] != (1, 2, 3)
        for x in range(0, ov.game.width, 40)
        for y in range(0, ov.game.height, 40)
    )
    assert changed
