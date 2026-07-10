"""Hand-rolled widgets (no ext menu library) so the display is fully ours."""
import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..core import Game


class Button:
    """A clickable rectangle with a centered label and a hover highlight."""

    def __init__(self, game: "Game", center: tuple[int, int],
                 size: tuple[int, int],
                 label: str, font: pygame.font.Font) -> None:
        """Build the button rect from a centre and size, label and font."""
        self.game = game
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.label = label
        self.font = font
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Update hover; return True on a left click inside the button."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
              and self.rect.collidepoint(event.pos)):
            return True
        return False

    def render(self, surface: pygame.Surface) -> None:
        """Draw the button (hover-highlighted) with its centered label."""
        colors = self.game.parser.get_ui_cfg()
        color = colors["button_hover"] if self.hovered \
            else colors["button_idle"]
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, colors["button_border"], self.rect, width=2,
                         border_radius=6)
        text = self.font.render(self.label, True, colors["text"])
        text_rect = text.get_rect()
        text_rect.center = self.rect.center
        surface.blit(text, text_rect)


class TextInput:
    """A single-line text field constrained for highscore name entry."""

    def __init__(self, game: "Game", center: tuple[int, int],
                 size: tuple[int, int],
                 font: "pygame.font.Font | None",
                 max_length: int = 10) -> None:
        """Build the input box with its geometry, font and max length."""
        self.game = game
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.font = font
        self.max_length = max_length
        self._value = ""

    @property
    def value(self) -> str:
        """Current validated text content."""
        return self._value

    def feed_char(self, ch: str) -> None:
        """Append one char if allowed (ASCII alnum/space, under max len)."""
        if len(self._value) >= self.max_length:
            return
        if not (ch.isascii() and (ch.isalnum() or ch == " ")):
            return
        self._value += ch

    def backspace(self) -> None:
        """Delete the last character, if any."""
        self._value = self._value[:-1]

    def handle_event(self, event: pygame.event.Event) -> None:
        """Map a KEYDOWN to a value edit; ignore other events."""
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_BACKSPACE:
            self.backspace()
        else:
            self.feed_char(event.unicode)

    def render(self, surface: pygame.Surface) -> None:
        """Draw the field box and the current text with a caret."""
        colors = self.game.parser.get_ui_cfg()
        pygame.draw.rect(surface, colors["button_idle"], self.rect,
                         border_radius=6)
        pygame.draw.rect(surface, colors["button_border"], self.rect, width=2,
                         border_radius=6)
        if self.font is None:
            return
        text = self.font.render(self._value + "_", True, colors["text"])
        surface.blit(text, text.get_rect(
            midleft=(self.rect.left + 8, self.rect.centery)))
