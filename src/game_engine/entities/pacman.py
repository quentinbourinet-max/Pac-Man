"""Pac-Man entity: player position, buffered movement and animation."""

import pygame
from game_engine.tools.level_tools import LevelTools
from game_engine.config import get_ui_cfg, Paths


class Pacman:
    """The player avatar: grid movement, direction buffering, animation."""

    def __init__(self, spawn_coord: list[int] | None = None,
                 speed: float = 4.0) -> None:
        self.speed = speed
        self.spawn_coord = list(spawn_coord) if spawn_coord else [9, 9]
        self.anim_delay = 0.08
        self.frames: list[pygame.Surface] | None = []
        self.load_sprites()
        self.reset()

    def reset(self) -> None:
        """Reset Pac-Man to its spawn cell (centre of the current maze)."""
        self.coord = list(self.spawn_coord)
        self.dir = "NONE"
        self.next_dir = "NONE"
        self.last_dir = "RIGHT"
        self.move_timer = 0.0
        self.anim_timer = 0.0
        self.frame_index = 0

    def load_sprites(self) -> None:
        """Load the Pac-Man sprite frames used for animation."""
        try:
            img1 = pygame.image.load(str(Paths.SPRITES /
                                         "1.png")).convert_alpha()
            img2 = pygame.image.load(str(Paths.SPRITES /
                                         "2.png")).convert_alpha()
            img3 = pygame.image.load(str(Paths.SPRITES /
                                         "3.png")).convert_alpha()
            self.frames = [img1, img2, img3, img2]
        except FileNotFoundError:
            print(" /!\\ Pac-Man sprites not found."
                  " Drawing a yellow circle instead.")
            self.frames = None

    def handle_input(self, direction: str) -> None:
        """Store the player's intended direction."""
        self.next_dir = direction

    def update(self, framesync: float, tools: LevelTools) -> bool:
        """
        Update timers and animation, and handle movement on the grid.
        Return True if Pac-Man moves to a new grid cell on this frame.
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
        """Compute the pixel position (without screen offset)
        for collision handling."""
        interval = 1.0 / self.speed
        progress = self.move_timer / interval
        smooth_offset_x = 0.0
        smooth_offset_y = 0.0
        if self.dir != "NONE":
            dc, dr = tools.DIR_MAP[self.dir]
            smooth_offset_x = -dc * (1.0 - progress) * tile_size
            smooth_offset_y = -dr * (1.0 - progress) * tile_size
        pac_pixel_x = self.coord[0] * tile_size + smooth_offset_x
        pac_pixel_y = self.coord[1] * tile_size + smooth_offset_y
        return pac_pixel_x, pac_pixel_y

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int,
               tile_size: int, tools: LevelTools) -> None:
        """Draw Pac-Man on screen."""
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
            pygame.draw.circle(surface, get_ui_cfg()["pacman"],
                               (int(screen_x + tile_size // 2),
                                int(screen_y + tile_size // 2)),
                               tile_size // 2)
