"""Game-over / victory scene with highscore name entry."""

import pygame
from typing import TYPE_CHECKING
from ..definitions import Scene
from ..ui.components import TextInput
from ..tools import highscore
from ..ui.theme import background

if TYPE_CHECKING:
    from ..core import Game


class EndScreen(Scene):
    """Shows the outcome + final score, takes a name, saves the highscore."""

    def __init__(self, game: "Game") -> None:
        """Read the outcome and final score, build the name-entry field."""
        super().__init__(game)
        self.score = getattr(game, "final_score", 0)
        self.won = getattr(game, "final_won", False)
        self.mode = game.mode
        size = max(18, game.height // 28)
        try:
            font_path = str(self.game.config.paths.font)
            self.font = pygame.font.Font(font_path, size)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.SysFont("monospace", size)
        field_w = max(200, game.width // 3)
        self.input = TextInput(self.game, (game.width // 2, game.height // 2),
                               (field_w, size * 2), self.font, max_length=10)

    @property
    def heading(self) -> str:
        """Title line depending on the outcome (victory vs game over)."""
        return "VICTORY!" if self.won else "GAME OVER"

    def submit(self) -> None:
        """Save the entered (or default) name + score to the highscore file."""
        name = self.input.value.strip()
        highscore.save(self.game.parser, self.mode, name, self.score)

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
        colors = self.game.parser.get_ui_cfg()
        surface.fill(background(self.game.parser, self.game.mode,
                                colors["bg"]))
        cx = self.game.width // 2
        head_color = colors["win"] if self.won else colors["lose"]
        head = self.font.render(self.heading, True, head_color)
        surface.blit(head, head.get_rect(center=(cx, self.game.height // 4)))
        score = self.font.render(f"SCORE: {self.score}", True, colors["text"])
        surface.blit(score, score.get_rect(center=(cx, self.game.height // 3)))
        prompt = self.font.render("ENTER YOUR NAME:", True, colors["text"])
        surface.blit(prompt, prompt.get_rect(
            center=(cx, self.game.height // 2 - self.input.rect.height)))
        self.input.render(surface)
        hint = self.font.render("PRESS ENTER", True, colors["text"])
        surface.blit(hint, hint.get_rect(
            center=(cx, self.game.height * 3 // 4)))
