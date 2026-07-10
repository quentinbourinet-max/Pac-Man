"""How-to-play screen: controls, configuration and credits."""

from typing import TYPE_CHECKING
import pygame
from ..definitions import Scene
from ..ui.theme import background
from ..ui.components import Button

if TYPE_CHECKING:
    from ..core import Game


class InstructionsMenu(Scene):
    """How-to-play + credits screen. ESC or click returns to the menu."""

    def __init__(self, game: "Game") -> None:
        """Load the instruction sections and build the responsive layout."""
        super().__init__(game)
        self.sections = self.game.parser.config.instructions
        h = game.height
        self.title_font = self._load_font(max(28, h // 22), bold=True)
        self.header_font = self._load_font(max(16, h // 42))
        self.body_font = self._load_font(max(13, h // 52))
        self.hint_font = self._load_font(max(12, h // 60))
        self._last_width = game.width
        self._last_height = game.height
        self.build_ui()

    def _load_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """Load the pixel font at a size, falling back to a system font."""
        try:
            return pygame.font.Font(str(self.game.parser.get_font_path()),
                                    size)
        except (FileNotFoundError, pygame.error):
            return pygame.font.SysFont("monospace", size, bold=bold)

    def build_ui(self) -> None:
        """Build the UI components with responsive sizes and margins."""
        title_size = max(24, self.game.height // 16)
        header_size = max(16, self.game.height // 30)
        body_size = max(12, self.game.height // 40)
        hint_size = max(10, self.game.height // 50)

        try:
            self.title_font = pygame.font.Font(str(
                self.game.parser.get_font_path()), title_size)
            self.header_font = pygame.font.Font(str(
                self.game.parser.get_font_path()), header_size)
            self.body_font = pygame.font.Font(str(
                self.game.parser.get_font_path()), body_size)
            self.hint_font = pygame.font.Font(str(
                self.game.parser.get_font_path()), hint_size)
        except (FileNotFoundError, pygame.error):
            self.title_font = pygame.font.SysFont("monospace", title_size,
                                                  bold=True)
            self.header_font = pygame.font.SysFont("monospace", header_size,
                                                   bold=True)
            self.body_font = pygame.font.SysFont("monospace", body_size)
            self.hint_font = pygame.font.SysFont("monospace", hint_size)
        margin_x = max(10, self.game.width // 40)
        margin_y = max(10, self.game.height // 40)
        button_width = max(120, self.game.width // 8)
        button_height = max(35, self.game.height // 16)
        cx = margin_x + (button_width // 2)
        cy = margin_y + (button_height // 2)
        self.back_btn = Button(self.game, (cx, cy), (button_width,
                                                     button_height),
                               "MENU", self.header_font)

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
        """Draw the controls / cheats / configuration / credits sections."""
        colors = self.game.parser.get_ui_cfg()
        surface.fill(background(self.game.parser, self.game.mode,
                                colors["bg_instructions"]))
        cx = self.game.width // 2

        title_cy = self.game.height // 10
        title = self.title_font.render("HOW TO PLAY", True, colors["title"])
        surface.blit(title, title.get_rect(center=(cx, title_cy)))

        header_h = self.header_font.get_height()
        body_h = self.body_font.get_height()
        gap = header_h // 2
        head_pad = header_h // 4
        body_step = body_h + 4

        total = sum(gap + header_h + head_pad + len(lines) * body_step
                    for _, lines in self.sections.items())
        top = title_cy + title.get_height() // 2
        hint_cy = self.game.height - 34
        y = top + max(10, (hint_cy - body_h - top - total) // 2)

        for header, lines in self.sections.items():
            y += gap
            head = self.header_font.render(header, True, colors["header"])
            surface.blit(head, head.get_rect(midtop=(cx, y)))
            y += header_h + head_pad
            for line in lines:
                text = self.body_font.render(line, True, colors["text"])
                surface.blit(text, text.get_rect(midtop=(cx, y)))
                y += body_step
        self.back_btn.render(surface)
