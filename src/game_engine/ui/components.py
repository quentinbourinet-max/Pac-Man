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


# =============================================================================
