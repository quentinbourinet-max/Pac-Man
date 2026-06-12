"""Main menu scene."""

from typing import TYPE_CHECKING

import pygame

from ..definitions import QUIT, Scene
from ..ui.components import Button

if TYPE_CHECKING:
    from ..core import Game

BG_COLOR = (10, 10, 30)
TITLE_COLOR = (255, 215, 0)


class MainMenu(Scene):
    """Landing screen. Buttons request transitions to other scenes."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.title_font = pygame.font.SysFont("monospace", 48, bold=True)
        font = pygame.font.SysFont("monospace", 22)

        cx = game.width // 2
        entries = [("CREDITS", "credits"), ("PLAY", "level"), ("QUIT", QUIT)]
        self.buttons: list[tuple[Button, str]] = []
        for i, (label, target) in enumerate(entries):
            btn = Button((cx, 240 + i * 70), (220, 50), label, font)
            self.buttons.append((btn, target))

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return QUIT
            for btn, target in self.buttons:
                if btn.handle_event(event):
                    return target
        return None

    def update(self, framesync: float) -> None:
        ...

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        title = self.title_font.render("PAC-MAN", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(self.game.width // 2, 120)))
        for btn, _ in self.buttons:
            btn.render(surface)


# =============================================================================
