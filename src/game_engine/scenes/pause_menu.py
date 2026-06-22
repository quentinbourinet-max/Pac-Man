"""Pause menu scene drawn over a frozen snapshot of the play scene."""

import pygame
from pathlib import Path
from typing import TYPE_CHECKING
from ..definitions import Scene
from ..ui.components import Button

if TYPE_CHECKING:
    from ..core import Game

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"


class PauseMenu(Scene):
    """Pause screen drawn over a frozen snapshot: Resume / Return to menu."""

    def __init__(self, game: "Game",
                 background_surface: pygame.Surface) -> None:
        super().__init__(game)
        self.background_surface = background_surface
        cx = self.game.width // 2
        button_width = max(200, self.game.width // 3)
        button_height = max(40, self.game.height // 12)
        title_size = max(32, self.game.height // 10)
        font_size = max(14, self.game.height // 25)
        try:
            self.title_font = pygame.font.Font(str(FONT_PATH), title_size)
            font = pygame.font.Font(str(FONT_PATH), font_size)
        except (FileNotFoundError, pygame.error):
            self.title_font = pygame.font.SysFont("monospace", title_size,
                                                  bold=True)
            font = pygame.font.SysFont("monospace", font_size)
        self.btn_resume = Button((cx, self.game.height // 2 - 40),
                                 (button_width, button_height),
                                 "RESUME", font)
        self.btn_menu = Button((cx, self.game.height // 2 + 50),
                               (button_width, button_height),
                               "MAIN MENU", font)

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        """ESC/Resume returns to play; Return-to-menu swaps to main menu."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.resume_game()
                    return None
            if self.btn_resume.handle_event(event):
                self.game.resume_game()
                return None
            if self.btn_menu.handle_event(event):
                self.game.change_scene("main_menu")
                return None
        return None

    def update(self, framesync: float) -> None:
        """Paused: the underlying scene is frozen, nothing to update."""
        pass

    def render(self, surface: pygame.Surface) -> None:
        """Draw the frozen snapshot dimmed, then the pause buttons."""
        surface.blit(self.background_surface, (0, 0))
        overlay = pygame.Surface((self.game.width, self.game.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        title = self.title_font.render("PAUSE", True, (255, 215, 0))
        surface.blit(title, title.get_rect(center=(self.game.width // 2,
                                                   self.game.height // 4)))
        self.btn_resume.render(surface)
        self.btn_menu.render(surface)
