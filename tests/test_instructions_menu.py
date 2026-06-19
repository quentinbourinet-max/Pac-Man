"""TDD for the InstructionsMenu scene (J2b / M49 / M56)."""

import pygame

from game_engine.scenes.instructions_menu import InstructionsMenu, INSTRUCTIONS


class FakeGame:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600


def make_instructions() -> InstructionsMenu:
    pygame.font.init()
    return InstructionsMenu(FakeGame())


def test_escape_returns_to_main_menu() -> None:
    im = make_instructions()
    ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    assert im.handle_events([ev]) == "main_menu"


def test_click_returns_to_main_menu() -> None:
    im = make_instructions()
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
    assert im.handle_events([ev]) == "main_menu"


def test_content_lists_controls_and_config() -> None:
    blob = " ".join(INSTRUCTIONS).lower()
    assert "wasd" in blob
    assert "config" in blob


def test_content_lists_cheat_keys() -> None:
    blob = " ".join(INSTRUCTIONS).lower()
    assert "f1" in blob
    assert "f2" in blob


def test_render_draws_onto_surface() -> None:
    im = make_instructions()
    surface = pygame.Surface((im.game.width, im.game.height))
    surface.fill((1, 2, 3))
    im.render(surface)
    changed = any(
        surface.get_at((x, y))[:3] != (1, 2, 3)
        for x in range(0, im.game.width, 40)
        for y in range(0, im.game.height, 40)
    )
    assert changed
