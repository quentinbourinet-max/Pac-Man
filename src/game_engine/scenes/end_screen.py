"""Game-over / victory scene with highscore name entry."""

import pygame
from pathlib import Path
from typing import TYPE_CHECKING
from ..definitions import Scene
from ..ui.components import TextInput
from ..tools import highscore
from ..ui.theme import background
from ..config import get_highscore_path

if TYPE_CHECKING:
    from ..core import Game

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"

BG_COLOR = (10, 10, 30)
TEXT_COLOR = (255, 255, 255)
WIN_COLOR = (255, 215, 0)
LOSE_COLOR = (220, 60, 60)
DEFAULT_NAME = "PLAYER"


class EndScreen(Scene):
    """Shows the outcome + final score, takes a name, saves the highscore."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.score = getattr(game, "final_score", 0)
        self.won = getattr(game, "final_won", False)
        self.highscore_path = get_highscore_path(game.mode)
        size = max(18, game.height // 28)
        try:
            self.font = pygame.font.Font(str(FONT_PATH), size)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.SysFont("monospace", size)
        field_w = max(200, game.width // 3)
        self.input = TextInput((game.width // 2, game.height // 2),
                               (field_w, size * 2), self.font, max_length=10)

    @property
    def heading(self) -> str:
        """Title line depending on the outcome (victory vs game over)."""
        return "VICTORY!" if self.won else "GAME OVER"

    def submit(self) -> None:
        """Save the entered (or default) name + score to the highscore file."""
        name = self.input.value.strip() or DEFAULT_NAME
        highscore.save(self.highscore_path, name, self.score)

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        """Feed typing into the name field; Enter saves and returns to menu."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.submit()
                return "main_menu"
            self.input.handle_event(event)
        return None

    def update(self, framesync: float) -> None:
        """No timed logic on this screen."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """Draw outcome, final score and the name-entry field."""
        surface.fill(background(self.game.mode, BG_COLOR))
        cx = self.game.width // 2
        head_color = WIN_COLOR if self.won else LOSE_COLOR
        head = self.font.render(self.heading, True, head_color)
        surface.blit(head, head.get_rect(center=(cx, self.game.height // 4)))
        score = self.font.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        surface.blit(score, score.get_rect(center=(cx, self.game.height // 3)))
        prompt = self.font.render("ENTER YOUR NAME:", True, TEXT_COLOR)
        surface.blit(prompt, prompt.get_rect(
            center=(cx, self.game.height // 2 - self.input.rect.height)))
        self.input.render(surface)
        hint = self.font.render("PRESS ENTER", True, TEXT_COLOR)
        surface.blit(hint, hint.get_rect(
            center=(cx, self.game.height * 3 // 4)))
