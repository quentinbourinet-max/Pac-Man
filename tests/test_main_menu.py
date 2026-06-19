"""TDD for MainMenu navigation entries (J2 / M49)."""

import pygame

from game_engine.scenes.main_menu import MainMenu


class FakeGame:
    def __init__(self) -> None:
        self.width = 800
        self.height = 600


def make_menu() -> MainMenu:
    pygame.font.init()
    return MainMenu(FakeGame())


def click(mm: MainMenu, target: str) -> str | None:
    btn = next(b for b, t in mm.buttons if t == target)
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                            pos=btn.rect.center)
    return mm.handle_events([ev])


def test_highscores_button_targets_scores() -> None:
    mm = make_menu()
    assert click(mm, "scores") == "scores"


def test_play_button_still_targets_level() -> None:
    mm = make_menu()
    assert click(mm, "level") == "level"


def test_instructions_button_targets_instructions() -> None:
    mm = make_menu()
    assert click(mm, "instructions") == "instructions"
