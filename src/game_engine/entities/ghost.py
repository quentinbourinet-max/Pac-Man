from typing import List
import pygame
from game_engine.tools.level_tools import LevelTools
from game_engine.tools.ghost_ai import GhostAI


class Ghost:

    def __init__(self, spawn_coord, color, name):
        self.name = name
        self.spawn_coord = list(spawn_coord)
        self.coord = list(spawn_coord)
        self.color = color
        self.frightened_color = (50, 150, 255)
        self.dir = "NONE"
        self.move_timer = 0.0
        self.state = "normal"
        self.ai = GhostAI()

    def update(self, framesync, base_speed, tools: LevelTools,
               pacman_coord: List[int], pacman_dir: str):
        """Gère le déplacement du fantôme à chaque frame."""
        current_interval = 1.0 / (base_speed * 2.0) if \
            self.state == "mort" else 1.0 / base_speed
        self.move_timer += framesync
        if self.move_timer >= current_interval:
            self.move_timer -= current_interval
            if self.state == "mort":
                self.dir = self.ai.find_next_move(self.coord,
                                                  self.spawn_coord,
                                                  tools, self.dir)
            elif self.state == "appeure":
                self.dir = self.ai.get_flee_direction(self.coord, pacman_coord,
                                                      tools, self.dir)
            else:
                if self.name == "Inky":
                    self.dir = self.ai.get_random_move(self.coord, tools,
                                                       self.dir)
                else:
                    target = self._get_chase_target(pacman_coord, pacman_dir,
                                                    tools)
                    self.dir = self.ai.find_next_move(self.coord, target,
                                                      tools, self.dir)
            if self.dir != "NONE":
                dc, dr = tools.DIR_MAP[self.dir]
                self.coord[0] += dc
                self.coord[1] += dr
            if self.state == "mort" and self.coord == self.spawn_coord:
                self.state = "normal"
                self.dir = "NONE"

    def _get_chase_target(self, pacman_coord: list[int], pacman_dir: str,
                          tools: LevelTools) -> list[int]:
        max_col = len(tools.grid[0]) - 1
        max_row = len(tools.grid) - 1
        target = list(pacman_coord)

        if self.name == "Blinky":
            target = list(pacman_coord)
        elif self.name == "Pinky":
            dc, dr = tools.DIR_MAP.get(pacman_dir, (0, 0))
            target = [pacman_coord[0] + 4 * dc, pacman_coord[1] + 4 * dr]
        elif self.name == "Clyde":
            dist = abs(self.coord[0] - pacman_coord[0]) + abs(self.coord[1] -
                                                              pacman_coord[1])
            if dist > 8:
                target = list(pacman_coord)
            else:
                target = [0, max_row]
        target[0] = max(0, min(target[0], max_col))
        target[1] = max(0, min(target[1], max_row))
        return target

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int,
               tile_size: int, ghost_speed: float, tools: LevelTools):
        """S'occupe de dessiner entièrement le fantôme à l'écran
        (avec interpolation)."""
        current_interval = 1.0 / (ghost_speed * 2.0) if self.state == "mort" \
            else 1.0 / ghost_speed
        g_progress = self.move_timer / current_interval
        g_so_x = -tools.DIR_MAP[self.dir][0] * (1.0 - g_progress) * tile_size \
            if self.dir != "NONE" else 0
        g_so_y = -tools.DIR_MAP[self.dir][1] * (1.0 - g_progress) * tile_size \
            if self.dir != "NONE" else 0
        gx = offset_x + self.coord[0] * tile_size + g_so_x
        gy = offset_y + self.coord[1] * tile_size + g_so_y
        cx, cy = int(gx + tile_size // 2), int(gy + tile_size // 2)
        if self.state != "mort":
            current_color = self.frightened_color if self.state == "appeure" \
                else self.color
            pygame.draw.circle(surface, current_color, (cx, cy),
                               tile_size // 2)
            pygame.draw.rect(surface, current_color, (gx, cy, tile_size,
                                                      tile_size // 2))
        eye_offset_x = int(tile_size * 0.15) if self.state == "appeure" \
            else int(tile_size * 0.2)
        eye_offset_y = int(tile_size * 0.1)
        eye_radius = max(1, int(tile_size * 0.1)) if self.state == "appeure" \
            else max(1, int(tile_size * 0.15))
        pupil_radius = max(1, int(tile_size * 0.05))
        look_x, look_y = 0, 0
        if self.state != "appeure":
            if self.dir == "RIGHT":
                look_x = pupil_radius
            elif self.dir == "LEFT":
                look_x = -pupil_radius
            elif self.dir == "UP":
                look_y = -pupil_radius
            elif self.dir == "DOWN":
                look_y = pupil_radius
        pygame.draw.circle(surface, (255, 255, 255),
                           (cx - eye_offset_x, cy - eye_offset_y), eye_radius)
        pygame.draw.circle(surface, (255, 255, 255),
                           (cx + eye_offset_x, cy - eye_offset_y), eye_radius)
        if self.state != "appeure":
            pygame.draw.circle(surface, (0, 0, 255),
                               (cx - eye_offset_x + look_x, cy -
                                eye_offset_y + look_y), pupil_radius)
            pygame.draw.circle(surface, (0, 0, 255),
                               (cx + eye_offset_x + look_x, cy -
                                eye_offset_y + look_y), pupil_radius)
