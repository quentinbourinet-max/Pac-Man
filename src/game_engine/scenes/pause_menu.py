import pygame
from ..definitions import Scene


class PauseMenu(Scene):
    def __init__(self, game, background_surface) -> None:
        super().__init__(game)
        self.background_surface = background_surface  # L'image du jeu figé
        self.selection = 0  # 0: Reprendre, 1: Menu

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "playing"
                elif event.key in (pygame.K_UP,
                                   pygame.K_DOWN,
                                   pygame.K_w,
                                   pygame.K_s):
                    self.selection = 1 - self.selection
                elif event.key == pygame.K_RETURN:
                    if self.selection == 0:
                        self.game.resume_game()
                    else:
                        self.game.change_scene("main_menu")
        return None

    def update(self, framesync: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.background_surface, (0, 0))
        overlay = pygame.Surface((self.game.width, self.game.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 48)
        title = font.render("PAUSE", True, (255, 255, 255))
        resume = font.render("> Reprendre" if self.selection == 0 else
                             "  Reprendre", True, (255, 255, 0))
        menu = font.render("> Menu" if self.selection == 1 else "  Menu", True,
                           (255, 255, 0))
        surface.blit(title, title.get_rect(center=(self.game.width//2, 100)))
        surface.blit(resume, resume.get_rect(center=(self.game.width//2, 250)))
        surface.blit(menu, menu.get_rect(center=(self.game.width//2, 300)))
