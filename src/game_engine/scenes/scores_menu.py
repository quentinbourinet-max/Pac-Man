"""Top-10 highscore board scene."""

import pygame
from pathlib import Path
from typing import TYPE_CHECKING
from ..definitions import Scene
from ..tools import highscore
from ..ui.theme import background
from ..config import get_highscore_path
from ..ui.components import Button
if TYPE_CHECKING:
    from ..core import Game

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"
BG_COLOR = (10, 10, 30)
TITLE_COLOR = (255, 215, 0)
TEXT_COLOR = (255, 255, 0)
HINT_COLOR = (150, 150, 150)


class ScoresMenu(Scene):
    """Reads the persisted board and renders the Top 10."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.highscore_path = get_highscore_path(game.mode)
        self.entries: list[dict[str, int | str]] = []
        self.refresh()
        size = max(18, game.height // 22)
        try:
            self.font = pygame.font.Font(str(FONT_PATH), size)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.SysFont("monospace", size)
        self._last_width = game.width
        self._last_height = game.height
        self.build_ui()

    def build_ui(self) -> None:
        """Build the UI components with responsive sizes and margins."""
        margin_x = max(10, self.game.width // 40)
        margin_y = max(10, self.game.height // 40)
        button_width = max(120, self.game.width // 8)
        button_height = max(35, self.game.height // 16)
        cx = margin_x + (button_width // 2)
        cy = margin_y + (button_height // 2)
        self.back_btn = Button((cx, cy), (button_width, button_height),
                               "MENU", self.font)

    def refresh(self) -> None:
        """Reload the board from disk and keep the top 10 by score."""
        board = highscore.load(self.highscore_path)
        self.entries = sorted(board, key=lambda e: e["score"],
                              reverse=True)[:10]

    def rows(self) -> list[str]:
        """Format the Top-10 as display lines (or a placeholder if empty)."""
        if not self.entries:
            return ["NO SCORES YET"]
        return [f"{i + 1}. {e['name']}  {e['score']}"
                for i, e in enumerate(self.entries)]

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        """Any ESC or click returns to the main menu."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "main_menu"
            if self.back_btn.handle_event(event):
                return "main_menu"
        return None

    def update(self, framesync: float) -> None:
        """Rebuild layout if window size changed."""
        if self.game.width != self._last_width or \
                self.game.height != self._last_height:
            self._last_width = self.game.width
            self._last_height = self.game.height
            self.build_ui()

    def render(self, surface: pygame.Surface) -> None:
        """Draw the Top-10 board title and columns beautifully aligned."""
        surface.fill(background(self.game.mode, BG_COLOR))
        cx = self.game.width // 2
        title = self.font.render("HIGH SCORES", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(cx, self.game.height // 8)))
        step = self.font.get_height() + 8
        start_y = self.game.height // 4
        if not self.entries:
            text = self.font.render("NO SCORES YET", True, "red")
            surface.blit(text, text.get_rect(center=(cx, start_y)))
        else:
            board_width = max(400, self.game.width // 2)
            left_x = cx - board_width // 2
            right_x = cx + board_width // 2
            name_x = left_x + max(60, board_width // 6)
            for i, e in enumerate(self.entries):
                y = start_y + i * step
                rank_str = f"{i + 1}."
                rank_surface = self.font.render(rank_str, True, "red")
                rank_rect = rank_surface.get_rect(left=left_x, top=y)
                surface.blit(rank_surface, rank_rect)
                name_str = str(e["name"])
                name_surface = self.font.render(name_str, True, "white")
                name_rect = name_surface.get_rect(left=name_x, top=y)
                surface.blit(name_surface, name_rect)
                score_str = str(e["score"])
                score_surface = self.font.render(score_str, True, "blue")
                score_rect = score_surface.get_rect(right=right_x, top=y)
                surface.blit(score_surface, score_rect)
        self.back_btn.render(surface)
