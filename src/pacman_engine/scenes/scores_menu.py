"""Top-10 highscore board scene."""

import pygame
from typing import TYPE_CHECKING
from ..definitions import Scene
from ..tools import highscore
from ..ui.theme import background
from ..ui.components import Button

if TYPE_CHECKING:
    from ..core import Game


class ScoresMenu(Scene):
    """Reads the persisted board and renders the Top 10."""

    def __init__(self, game: "Game") -> None:
        """Load the active mode's board and build the responsive layout."""
        super().__init__(game)
        self.mode = game.mode
        self.entries: list[dict[str, int | str]] = []
        self.refresh()
        size = max(18, game.height // 22)
        try:
            self.font = pygame.font.Font(str(
                self.game.parser.get_font_path()), size)
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
        self.back_btn = Button(self.game, (cx, cy), (button_width,
                                                     button_height),
                               "MENU", self.font)

    def refresh(self) -> None:
        """Reload the board from disk and keep the top 10 by score."""
        board = highscore.load(self.game.parser, self.mode)
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
        colors = self.game.parser.get_ui_cfg()
        surface.fill(background(self.game.parser, self.game.mode,
                                colors["bg"]))
        cx = self.game.width // 2
        title = self.font.render("HIGH SCORES", True, colors["title"])
        surface.blit(title, title.get_rect(center=(cx, self.game.height // 8)))
        step = self.font.get_height() + 8
        start_y = self.game.height // 4
        if not self.entries:
            text = self.font.render("NO SCORES YET", True, colors["lose"])
            surface.blit(text, text.get_rect(center=(cx, start_y)))
        else:
            board_width = max(400, self.game.width // 2)
            left_x = cx - board_width // 2
            right_x = cx + board_width // 2
            name_x = left_x + max(60, board_width // 6)
            for i, e in enumerate(self.entries):
                y = start_y + i * step
                rank_surface = self.font.render(f"{i + 1}.", True,
                                                colors["lose"])
                surface.blit(rank_surface,
                             rank_surface.get_rect(left=left_x, top=y))
                name_surface = self.font.render(str(e["name"]), True,
                                                colors["text"])
                surface.blit(name_surface,
                             name_surface.get_rect(left=name_x, top=y))
                score_surface = self.font.render(str(e["score"]), True,
                                                 colors["title"])
                surface.blit(score_surface,
                             score_surface.get_rect(right=right_x, top=y))
        self.back_btn.render(surface)
