"""Game credits scene."""

from typing import TYPE_CHECKING

import pygame

from ..definitions import Scene

if TYPE_CHECKING:
    from ..core import Game

BG_COLOR = (30, 10, 10)
TEXT_COLOR = (255, 255, 255)
HINT_COLOR = (150, 150, 150)
CREDITS = [
          "===============  PAC-MAN  ===============",
          "qbourine & jferone",
          "version 1.00",
          "",
          "============  MAZEGEN PACK  ============",
          "elocufie & jferone",
          "",
          "=============== FAN BASE ===============",
          "You <3"
          ]


class CreditsMenu(Scene):
    """Static credits screen. ESC or click returns to the main menu."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.font = pygame.font.SysFont("monospace", 24)
        self.hint_font = pygame.font.SysFont("monospace", 16)

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "main_menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "main_menu"
        return None

    def update(self, framesync: float) -> None:
        ...

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        cx = self.game.width // 2
        for i, line in enumerate(CREDITS):
            text = self.font.render(line, True, TEXT_COLOR)
            surface.blit(text, text.get_rect(center=(cx, 100 + i * 36)))
        hint = self.hint_font.render("ESC / click to go back", True,
                                     HINT_COLOR)
        surface.blit(hint, hint.get_rect(center=(cx, self.game.height - 30)))


# =============================================================================
