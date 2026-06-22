from pathlib import Path
import pygame
from game_engine.tools.level_tools import LevelTools

PACMAN_COLOR = (255, 255, 0)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
SPRITES_DIR = ROOT_DIR / "tools" / "visualisation_tools" / "pac-man_sprites"


class Pacman:
    def __init__(self) -> None:
        self.speed = 4.0
        self.anim_delay = 0.08
        self.frames = []
        self.load_sprites()
        self.reset()

    def reset(self) -> None:
        """Remet Pac-Man dans sa configuration initiale."""
        self.coord = [9, 9]
        self.dir = "NONE"
        self.next_dir = "NONE"
        self.last_dir = "RIGHT"
        self.move_timer = 0.0
        self.anim_timer = 0.0
        self.frame_index = 0

    def load_sprites(self) -> None:
        """Charge les images de Pac-Man pour les animations."""
        try:
            img1 = pygame.image.load(str(SPRITES_DIR /
                                         "1.png")).convert_alpha()
            img2 = pygame.image.load(str(SPRITES_DIR /
                                         "2.png")).convert_alpha()
            img3 = pygame.image.load(str(SPRITES_DIR /
                                         "3.png")).convert_alpha()
            self.frames = [img1, img2, img3, img2]
        except FileNotFoundError:
            print(" /!\\ Images de Pac-Man introuvables."
                  "Dessin d'un rond jaune par défaut.")
            self.frames = None

    def handle_input(self, direction: str) -> None:
        """Enregistre l'intention de direction du joueur."""
        self.next_dir = direction

    def update(self, framesync: float, tools: LevelTools) -> bool:
        """
        Met à jour les timers, l'animation et gère
        le déplacement sur la grille.
        Retourne True si Pac-Man change de case sur la grille à cette frame.
        """
        self.anim_timer += framesync
        if self.anim_timer >= self.anim_delay:
            self.anim_timer = 0.0
            if self.dir != "NONE":
                self.frame_index = (self.frame_index + 1) % 4
        self.move_timer += framesync
        interval = 1.0 / self.speed
        moved_tile = False

        if self.move_timer >= interval:
            self.move_timer -= interval
            if tools.is_move_possible(self.coord[0], self.coord[1],
                                      self.next_dir):
                self.dir = self.next_dir
            if tools.is_move_possible(self.coord[0], self.coord[1], self.dir):
                dc, dr = tools.DIR_MAP[self.dir]
                self.coord[0] += dc
                self.coord[1] += dr
                self.last_dir = self.dir
                moved_tile = True
            else:
                self.dir = "NONE"
        return moved_tile

    def get_pixel_pos(self, tile_size: int,
                      tools: LevelTools) -> tuple[float, float]:
        """Calcule la position en pixels (sans offset écran)
        pour la gestion des collisions."""
        interval = 1.0 / self.speed
        progress = self.move_timer / interval
        smooth_offset_x = 0
        smooth_offset_y = 0
        if self.dir != "NONE":
            dc, dr = tools.DIR_MAP[self.dir]
            smooth_offset_x = -dc * (1.0 - progress) * tile_size
            smooth_offset_y = -dr * (1.0 - progress) * tile_size
        pac_pixel_x = self.coord[0] * tile_size + smooth_offset_x
        pac_pixel_y = self.coord[1] * tile_size + smooth_offset_y
        return pac_pixel_x, pac_pixel_y

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int,
               tile_size: int, tools: LevelTools) -> None:
        """Dessine Pac-Man à l'écran."""
        pac_pixel_x, pac_pixel_y = self.get_pixel_pos(tile_size, tools)
        screen_x = offset_x + pac_pixel_x
        screen_y = offset_y + pac_pixel_y

        if self.frames:
            current_image = self.frames[self.frame_index]
            if self.last_dir == "LEFT":
                transformed_image = pygame.transform.flip(current_image,
                                                          True, False)
            else:
                angle = 0
                if self.last_dir == "UP":
                    angle = 90
                elif self.last_dir == "DOWN":
                    angle = -90
                transformed_image = pygame.transform.rotate(current_image,
                                                            angle)
            transformed_image = pygame.transform.scale(transformed_image,
                                                       (tile_size, tile_size))
            rect = transformed_image.get_rect(center=(int(screen_x +
                                                          tile_size // 2),
                                                      int(screen_y +
                                                          tile_size // 2)))
            surface.blit(transformed_image, rect)
        else:
            pygame.draw.circle(surface, PACMAN_COLOR,
                               (int(screen_x + tile_size // 2),
                                int(screen_y + tile_size // 2)),
                               tile_size // 2)
