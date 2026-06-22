"""How-to-play screen: controls, configuration and credits."""

from typing import TYPE_CHECKING
import pygame
from ..definitions import Scene

if TYPE_CHECKING:
    from ..core import Game

BG_COLOR = (30, 10, 10)
TITLE_COLOR = (255, 215, 0)
TEXT_COLOR = (255, 255, 255)
HINT_COLOR = (150, 150, 150)

INSTRUCTIONS = [
    "=============== CONTROLS ===============",
    "Move           Arrow keys / WASD / ZQSD",
    "Validate name  ENTER",
    "Back / quit    ESC",
    "",
    "============= CONFIGURATION =============",
    "data/config.json sets the game parameters:",
    "lives, level_max_time, points_per_*, seed,",
    "window size and the highscore filename.",
    "",
    "================= CHEATS =================",
    "F1  Toggle invincibility",
    "F2  Skip to next level",
    "",
    "================ CREDITS ================",
    "qbourine & jferone",
    "Mazegen pack: elocufie & jferone",
]


class InstructionsMenu(Scene):
    """How-to-play + credits screen. ESC or click returns to the menu."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.title_font = pygame.font.SysFont("monospace", 32, bold=True)
        self.font = pygame.font.SysFont("monospace", 20)
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
        title = self.title_font.render("HOW TO PLAY", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(cx, 60)))
        step = self.font.get_height() + 4
        for i, line in enumerate(INSTRUCTIONS):
            text = self.font.render(line, True, TEXT_COLOR)
            surface.blit(text, text.get_rect(center=(cx, 130 + i * step)))
        hint = self.hint_font.render("ESC / click to go back", True,
                                     HINT_COLOR)
        surface.blit(hint, hint.get_rect(center=(cx, self.game.height - 30)))
