"""Pause overlay: freezes the scene and offers Resume / Return to menu."""

from typing import TYPE_CHECKING
import pygame
from ..definitions import Overlay, CLOSE
from .components import Button

if TYPE_CHECKING:
    from ..core import Game

DIM_COLOR = (0, 0, 0)
DIM_ALPHA = 160
TITLE_COLOR = (255, 215, 0)


class PauseOverlay(Overlay):
    """Modal pause menu drawn over the frozen scene."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self._pause_music()
        font = pygame.font.SysFont("monospace", max(20, game.height // 24))
        self.title_font = pygame.font.SysFont(
            "monospace", max(32, game.height // 12), bold=True)
        cx = game.width // 2
        cy = game.height // 2
        width = max(220, game.width // 3)
        height = max(44, game.height // 12)
        gap = height + 20
        self.buttons: list[tuple[Button, str]] = [
            (Button((cx, cy), (width, height), "RESUME", font), CLOSE),
            (Button((cx, cy + gap), (width, height), "MAIN MENU", font),
             "main_menu"),
        ]

    def _pause_music(self) -> None:
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass

    def _resume_music(self) -> None:
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass

    def on_close(self) -> None:
        self._resume_music()

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        for event in events:
            if event.type == pygame.KEYDOWN and \
                    event.key in (pygame.K_ESCAPE, pygame.K_p):
                return CLOSE
            for btn, target in self.buttons:
                if btn.handle_event(event):
                    return target
        return None

    def render(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface((self.game.width, self.game.height))
        dim.set_alpha(DIM_ALPHA)
        dim.fill(DIM_COLOR)
        surface.blit(dim, (0, 0))
        title = self.title_font.render("PAUSED", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(
            center=(self.game.width // 2, self.game.height // 4)))
        for btn, _ in self.buttons:
            btn.render(surface)
