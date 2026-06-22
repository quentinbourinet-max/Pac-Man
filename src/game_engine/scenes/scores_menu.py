"""Top-10 highscore board scene."""

from pathlib import Path
from typing import TYPE_CHECKING
import pygame
from ..definitions import Scene
from ..tools import highscore
from ..config import get_highscore_path

if TYPE_CHECKING:
    from ..core import Game

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"
BG_COLOR = (10, 10, 30)
TITLE_COLOR = (255, 215, 0)
TEXT_COLOR = (255, 255, 255)
HINT_COLOR = (150, 150, 150)


class ScoresMenu(Scene):
    """Reads the persisted board and renders the Top 10."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.highscore_path = get_highscore_path()
        self.entries: list[dict[str, int | str]] = []
        self.refresh()
        size = max(18, game.height // 22)
        try:
            self.font = pygame.font.Font(str(FONT_PATH), size)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.SysFont("monospace", size)

    def refresh(self) -> None:
        board = highscore.load(self.highscore_path)
        self.entries = sorted(board, key=lambda e: e["score"],
                              reverse=True)[:10]

    def rows(self) -> list[str]:
        if not self.entries:
            return ["NO SCORES YET"]
        return [f"{i + 1}. {e['name']}  {e['score']}"
                for i, e in enumerate(self.entries)]

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
        title = self.font.render("HIGH SCORES", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(cx, self.game.height // 8)))
        step = self.font.get_height() + 6
        for i, line in enumerate(self.rows()):
            text = self.font.render(line, True, TEXT_COLOR)
            surface.blit(text, text.get_rect(
                center=(cx, self.game.height // 4 + i * step)))
        hint = self.font.render("ESC / click to go back", True, HINT_COLOR)
        surface.blit(hint, hint.get_rect(
            center=(cx, self.game.height - 30)))
