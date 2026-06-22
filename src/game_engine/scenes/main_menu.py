"""Main menu scene."""

import pygame
from typing import TYPE_CHECKING
from pathlib import Path
from ..definitions import QUIT, Scene
from ..ui.components import Button
from ..ui.theme import background
from ..config import get_cfg

if TYPE_CHECKING:
    from ..core import Game

MODE_TARGET = "__toggle_mode__"


def _available_modes() -> list[str]:
    """List configured game modes (every game.* preset except 'common')."""
    try:
        game = get_cfg().get("game", {})
        modes = [k for k in game
                 if k != "common" and isinstance(game[k], dict)]
        return modes or ["original"]
    except Exception:
        return ["original"]


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
        self.modes = _available_modes()
        if game.mode not in self.modes:
            game.mode = self.modes[0]
        try:
            self.font_path: str | None = str(FONT_PATH)
        except Exception:
            self.font_path = None
        self.build_ui()

    def _mode_label(self) -> str:
        """Label for the mode toggle reflecting the active mode."""
        return f"MODE: {self.game.mode.upper()}"

    def build_ui(self) -> None:
        """Build the UI scaled proportionally to the window size."""
        title_size = max(32, self.game.height // 10)
        font_size = max(16, self.game.height // 25)
        try:
            self.title_font = pygame.font.Font(self.font_path, title_size)
            font = pygame.font.Font(self.font_path, font_size)
        except (FileNotFoundError, pygame.error):
            print(f" /!\\ Font not found at {FONT_PATH}. Using default.")
            self.title_font = pygame.font.SysFont("monospace",
                                                  title_size, bold=True)
            font = pygame.font.SysFont("monospace", font_size)
        cx = self.game.width // 2
        button_width = max(200, self.game.width // 3)
        button_height = max(40, self.game.height // 12)
        start_y = self.game.height // 2 - (button_height // 2)
        spacing = button_height + max(10, self.game.height // 40)

        entries = [("PLAY", "level"),
                   (self._mode_label(), MODE_TARGET),
                   ("SCORES", "scores"),
                   ("HOW TO PLAY", "instructions"),
                   ("QUIT", QUIT)]
        self.buttons: list[tuple[Button, str]] = []
        for i, (label, target) in enumerate(entries):
            btn = Button((cx, start_y + i * spacing),
                         (button_width, button_height), label, font)
            self.buttons.append((btn, target))

    def _cycle_mode(self) -> None:
        """Advance to the next configured mode and refresh the toggle label."""
        idx = self.modes.index(self.game.mode) if \
            self.game.mode in self.modes else 0
        self.game.mode = self.modes[(idx + 1) % len(self.modes)]
        for btn, target in self.buttons:
            if target == MODE_TARGET:
                btn.label = self._mode_label()

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        """ESC quits; the MODE button cycles presets; others transition."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return QUIT
            for btn, target in self.buttons:
                if btn.handle_event(event):
                    if target == MODE_TARGET:
                        self._cycle_mode()
                        return None
                    return target
        return None

    def update(self, framesync: float) -> None:
        """Rebuild the layout if the window size changed."""
        if self.game.width != self._last_width or \
                self.game.height != self._last_height:
            self._last_width = self.game.width
            self._last_height = self.game.height
            self.build_ui()

    def render(self, surface: pygame.Surface) -> None:
        """Draw the title and the menu buttons."""
        surface.fill(background(self.game.mode, BG_COLOR))
        title = self.title_font.render("PAC-MAN", True, TITLE_COLOR)
        title_y = max(50, self.game.height // 5)
        surface.blit(title,
                     title.get_rect(center=(self.game.width // 2,
                                            title_y)))
        for btn, _ in self.buttons:
            btn.render(surface)
