"""Main menu scene."""

import pygame
from typing import TYPE_CHECKING
from pathlib import Path

from ..definitions import QUIT, Scene
from ..ui.components import Button

if TYPE_CHECKING:
    from ..core import Game

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"

BG_COLOR = (10, 10, 30)
TITLE_COLOR = (255, 215, 0)


class MainMenu(Scene):
    """Landing screen. Buttons request transitions to other scenes."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self._last_width = game.width
        self._last_height = game.height
        try:
            self.font_path = str(FONT_PATH)
        except Exception:
            self.font_path = None
        self.build_ui()

    def build_ui(self) -> None:
        """Construit l'interface
        proportionnellement à la taille de la fenêtre."""
        title_size = max(32, self.game.height // 10)
        font_size = max(16, self.game.height // 25)
        try:
            self.title_font = pygame.font.Font(self.font_path, title_size)
            font = pygame.font.Font(self.font_path, font_size)
        except (FileNotFoundError, pygame.error):
            print(f" /!\\ Police introuvable à {FONT_PATH}. Repli sur défaut.")
            self.title_font = pygame.font.SysFont("monospace",
                                                  title_size, bold=True)
            font = pygame.font.SysFont("monospace", font_size)
        cx = self.game.width // 2
        button_width = max(200, self.game.width // 3)
        button_height = max(40, self.game.height // 12)
        start_y = self.game.height // 2 - (button_height // 2)
        spacing = button_height + max(10, self.game.height // 20)

        entries = [("PLAY", "level"), ("HIGHSCORES", "scores"),
                   ("INSTRUCTIONS", "instructions"), ("QUIT", QUIT)]
        self.buttons: list[tuple[Button, str]] = []
        for i, (label, target) in enumerate(entries):
            btn = Button((cx, start_y + i * spacing),
                         (button_width, button_height), label, font)
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
        if self.game.width != self._last_width or \
                self.game.height != self._last_height:
            self._last_width = self.game.width
            self._last_height = self.game.height
            self.build_ui()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        title = self.title_font.render("PAC-MAN", True, TITLE_COLOR)
        title_y = max(50, self.game.height // 5)
        surface.blit(title,
                     title.get_rect(center=(self.game.width // 2,
                                            title_y)))
        for btn, _ in self.buttons:
            btn.render(surface)
