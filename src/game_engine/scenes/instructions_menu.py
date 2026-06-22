"""How-to-play screen: controls, configuration and credits."""

from pathlib import Path
from typing import TYPE_CHECKING
import pygame
from ..definitions import Scene
from ..ui.theme import background

if TYPE_CHECKING:
    from ..core import Game

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"

BG_COLOR = (30, 10, 10)
TITLE_COLOR = (255, 215, 0)
HEADER_COLOR = (255, 203, 71)
TEXT_COLOR = (235, 235, 235)
HINT_COLOR = (150, 150, 150)

# Each section is a header plus its body lines, rendered centered.
SECTIONS = [
    ("CONTROLS", [
        "Move :  arrow keys / WASD / ZQSD",
        "Pause / back :  ESC",
        "Validate name :  ENTER",
        "Fullscreen :  F11",
    ]),
    ("CHEATS", [
        "F1 :  toggle invincibility",
        "F2 :  skip to next level",
    ]),
    ("CONFIGURATION", [
        "data/ config. json   contains all game's settings",
        "data/ highscores. json   all your unsecured scores"
    ]),
    ("CREDITS", [
        "Pac-Man :   jferone & qbourine from @42nice",
        "Maze pack :   who knows..?   (  joy of Open Source c:  )",
    ]),
]


class InstructionsMenu(Scene):
    """How-to-play + credits screen. ESC or click returns to the menu."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        h = game.height
        self.title_font = self._load_font(max(28, h // 22), bold=True)
        self.header_font = self._load_font(max(16, h // 42))
        self.body_font = self._load_font(max(13, h // 52))
        self.hint_font = self._load_font(max(12, h // 60))

    def _load_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """Load the pixel font at a size, falling back to a system font."""
        try:
            return pygame.font.Font(str(FONT_PATH), size)
        except (FileNotFoundError, pygame.error):
            return pygame.font.SysFont("monospace", size, bold=bold)

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        """Any ESC or click returns to the main menu."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "main_menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "main_menu"
        return None

    def update(self, framesync: float) -> None:
        """Static screen: nothing to update."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """Draw the controls / cheats / configuration / credits sections."""
        surface.fill(background(self.game.mode, BG_COLOR))
        cx = self.game.width // 2

        title_cy = self.game.height // 10
        title = self.title_font.render("HOW TO PLAY", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(cx, title_cy)))

        header_h = self.header_font.get_height()
        body_h = self.body_font.get_height()
        gap = header_h // 2
        head_pad = header_h // 4
        body_step = body_h + 4

        total = sum(gap + header_h + head_pad + len(lines) * body_step
                    for _, lines in SECTIONS)
        top = title_cy + title.get_height() // 2
        hint_cy = self.game.height - 34
        y = top + max(10, (hint_cy - body_h - top - total) // 2)

        for header, lines in SECTIONS:
            y += gap
            head = self.header_font.render(header, True, HEADER_COLOR)
            surface.blit(head, head.get_rect(midtop=(cx, y)))
            y += header_h + head_pad
            for line in lines:
                text = self.body_font.render(line, True, TEXT_COLOR)
                surface.blit(text, text.get_rect(midtop=(cx, y)))
                y += body_step

        hint = self.hint_font.render("ESC / click to go back", True,
                                     HINT_COLOR)
        surface.blit(hint, hint.get_rect(center=(cx, hint_cy)))
