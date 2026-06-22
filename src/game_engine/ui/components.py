# == UI COMPONENTS ============================================================
# Hand-rolled widgets (no external menu library) so the display is fully ours.

import pygame

IDLE_COLOR = (40, 40, 40)
HOVER_COLOR = (70, 70, 90)
BORDER_COLOR = (255, 215, 0)
TEXT_COLOR = (255, 255, 255)


class Button:
    """A clickable rectangle with a centered label and a hover highlight."""

    def __init__(self, center: tuple[int, int], size: tuple[int, int],
                 label: str, font: pygame.font.Font) -> None:
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
        color = HOVER_COLOR if self.hovered else IDLE_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, width=2,
                         border_radius=6)
        text = self.font.render(self.label, True, TEXT_COLOR)
        surface.blit(text, text.get_rect(center=self.rect.center))


class TextInput:
    """A single-line text field constrained for highscore name entry."""

    def __init__(self, center: tuple[int, int], size: tuple[int, int],
                 font: "pygame.font.Font | None",
                 max_length: int = 10) -> None:
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.font = font
        self.max_length = max_length
        self._value = ""

    @property
    def value(self) -> str:
        return self._value

    def feed_char(self, ch: str) -> None:
        if len(self._value) >= self.max_length:
            return
        if not (ch.isascii() and (ch.isalnum() or ch == " ")):
            return
        self._value += ch

    def backspace(self) -> None:
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
        pygame.draw.rect(surface, IDLE_COLOR, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, width=2,
                         border_radius=6)
        if self.font is None:
            return
        text = self.font.render(self._value + "_", True, TEXT_COLOR)
        surface.blit(text, text.get_rect(
            midleft=(self.rect.left + 8, self.rect.centery)))
