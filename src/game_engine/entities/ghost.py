import random
import pygame
from game_engine.tools.level_tools import LevelTools


class Ghost:

    def __init__(self, spawn_coord, color):
        self.spawn_coord = list(spawn_coord)
        self.coord = list(spawn_coord)
        self.color = color
        self.frightened_color = (50, 150, 255)
        self.dir = "NONE"
        self.move_timer = 0.0
        self.state = "normal"

    def update(self, framesync, base_speed, tools: LevelTools):
        """Gère le déplacement du fantôme à chaque frame."""
        current_interval = 1.0 / (base_speed * 2.0) if \
            self.state == "mort" else 1.0 / base_speed
        self.move_timer += framesync
        if self.move_timer >= current_interval:
            self.move_timer -= current_interval
            if self.state == "mort":
                self._move_to_base(tools.DIR_MAP)
            else:
                self._move_normal(tools)

    def _move_to_base(self, dir_map):
        """Logique de retour à la base (ignore les murs)."""
        dx = self.spawn_coord[0] - self.coord[0]
        dy = self.spawn_coord[1] - self.coord[1]
        if dx == 0 and dy == 0:
            self.state = "normal"
            self.dir = "NONE"
        else:
            if abs(dx) > abs(dy):
                self.dir = "RIGHT" if dx > 0 else "LEFT"
            else:
                self.dir = "DOWN" if dy > 0 else "UP"
            dc, dr = dir_map[self.dir]
            self.coord[0] += dc
            self.coord[1] += dr

    def _move_normal(self, tools: LevelTools):
        """Logique de déplacement standard et apeuré (respecte les murs)."""
        possible_dirs = []
        for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if tools.is_move_possible(self.coord[0], self.coord[1], d):
                opposing = {"UP": "DOWN",
                            "DOWN": "UP",
                            "LEFT": "RIGHT",
                            "RIGHT": "LEFT"}
                if d != opposing.get(self.dir, "NONE") or self.dir == "NONE":
                    possible_dirs.append(d)
        if not possible_dirs:
            possible_dirs = [d for d in ["UP", "DOWN", "LEFT", "RIGHT"]
                             if tools.is_move_possible(self.coord[0],
                                                       self.coord[1], d)]
        current_still_possible = tools.is_move_possible(self.coord[0],
                                                        self.coord[1],
                                                        self.dir)
        if not current_still_possible or (len(possible_dirs) > 1 and
                                          random.random() < 0.3) or \
                self.dir == "NONE":
            if possible_dirs:
                self.dir = random.choice(possible_dirs)
            else:
                self.dir = "NONE"
        if self.dir != "NONE":
            dc, dr = tools.DIR_MAP[self.dir]
            self.coord[0] += dc
            self.coord[1] += dr

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
