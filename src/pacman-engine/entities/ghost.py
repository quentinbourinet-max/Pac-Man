"""Ghost entity: per-personality targeting AI and state machine."""

from typing import List, Dict
import pygame
from pathlib import Path
from game_engine.tools.level_tools import LevelTools
from game_engine.tools.ghost_ai import GhostAI
from ..tools.parser import ConfigParser


class Ghost:
    """One ghost: movement, normal/scared/dead states and chase targeting."""

    def __init__(self, spawn_coord: list[int],
                 color: tuple[int, int, int], name: str,
                 dead_speed_mult: float = 2.0,
                 parser: ConfigParser | None = None) -> None:
        self.name = name
        self.spawn_coord = list(spawn_coord)
        self.coord = list(spawn_coord)
        self.color = color
        self.frightened_color = (50, 150, 255)
        self.dir = "NONE"
        self.move_timer = 0.0
        self.state = "normal"
        self.dead_speed_mult = dead_speed_mult
        self.ai = GhostAI()
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.frames: Dict[str, List[pygame.Surface]] = {
            "UP": [],
            "DOWN": [],
            "LEFT": [],
            "RIGHT": []
        }
        if parser:
            self._load_sprites(parser)

    def _load_sprites(self, parser: ConfigParser) -> None:
        """Charge 3 images distinctes (_1.png, _2.png, _3.png)
        basées sur le chemin du config."""
        try:
            folder_path = getattr(parser.config.paths, "ghosts", None)

            if folder_path and pygame.display.get_init():
                ghost_name = self.name.lower()
                folder = Path(folder_path)

                dir_suffixes = ["up", "down", "left", "right"]

                for suffix in dir_suffixes:
                    pygame_key = suffix.upper()
                    for i in range(1, 3):
                        frame_path = folder / f"{ghost_name}_{suffix}_{i}.png"
                        frame = pygame.image.load(str(
                            frame_path)).convert_alpha()
                        self.frames[pygame_key].append(frame)  # type: ignore
                self.frames["SCARED"] = []
                for i in range(1, 3):
                    path = folder / f"scared_{i}.png"
                    self.frames["SCARED"].append(pygame.image.load(
                        str(path)).convert_alpha())  # type: ignore
        except Exception as e:
            print(f" /!\\ Can't load sprites for {self.name} : {e}")
            self.frames = {}

    def update(self, framesync: float, base_speed: float, tools: LevelTools,
               pacman_coord: List[int], pacman_dir: str,
               phase: str = "chase") -> None:
        """Handle the ghost's movement on each frame.

        ``phase`` is the global scatter/chase phase: in ``scatter`` a normal
        ghost heads to its home corner, in ``chase`` it uses its personality
        target. Inky always wanders randomly (deliberate design choice).
        """

        current_interval = 1.0 / (base_speed * self.dead_speed_mult) if \
            self.state == "dead" else 1.0 / base_speed

        # GHOST MOVEMENTS -----------------------------------------------------
        self.move_timer += framesync
        if self.move_timer >= current_interval:
            self.move_timer -= current_interval

            if self.state == "dead":
                self.dir = self.ai.find_next_move(self.coord,
                                                  self.spawn_coord,
                                                  tools, self.dir)

            elif self.state == "scared":
                self.dir = self.ai.get_flee_direction(self.coord,
                                                      pacman_coord,
                                                      tools, self.dir)

            elif self.name == "Inky":
                self.dir = self.ai.get_random_move(self.coord,
                                                   tools, self.dir)

            elif phase == "scatter":
                self.dir = self.ai.find_next_move(self.coord,
                                                  self.spawn_coord,
                                                  tools, self.dir)
                if self.dir == "NONE":
                    # Is already in its corner: keep milling around it
                    self.dir = self.ai.get_random_move(self.coord,
                                                       tools, self.dir)

            else:
                target = self._get_chase_target(pacman_coord,
                                                pacman_dir, tools)
                self.dir = self.ai.find_next_move(self.coord,
                                                  target,
                                                  tools, self.dir)

            if self.dir != "NONE":
                dc, dr = tools.DIR_MAP[self.dir]
                self.coord[0] += dc
                self.coord[1] += dr

            if self.state == "dead" and self.coord == self.spawn_coord:
                self.state = "normal"
                self.dir = "NONE"
        if self.frames:
            self.anim_timer += framesync
            if self.anim_timer >= 0.15:
                self.anim_timer = 0.0
                self.anim_frame = (self.anim_frame + 1) % 2

    def _get_chase_target(self, pacman_coord: list[int], pacman_dir: str,
                          tools: LevelTools) -> list[int]:
        """Return the target cell for this ghost's personality, clamped to
        the grid (Blinky=Pac-Man, Pinky=4 ahead, Clyde=Pac-Man if far)."""
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

    def render(self, surface: pygame.Surface,
               offset_x: int, offset_y: int,
               tile_size: int,
               ghost_speed: float,
               tools: LevelTools) -> None:
        """Render the ghost on screen (with interpolation)."""

        current_interval = 1.0 / (ghost_speed * self.dead_speed_mult) if \
            self.state == "dead" else 1.0 / ghost_speed

        # GHOST POSITION ------------------------------------------------------
        g_progress = self.move_timer / current_interval
        g_so_x = -tools.DIR_MAP[self.dir][0] * (1.0 - g_progress) * tile_size \
            if self.dir != "NONE" else 0
        g_so_y = -tools.DIR_MAP[self.dir][1] * (1.0 - g_progress) * tile_size \
            if self.dir != "NONE" else 0
        gx = offset_x + self.coord[0] * tile_size + g_so_x
        gy = offset_y + self.coord[1] * tile_size + g_so_y
        cx, cy = int(gx + tile_size // 2), int(gy + tile_size // 2)

        if self.frames:
            # 1. Choix du sprite selon l'état
            if self.state == "scared":
                sprite = self.frames["SCARED"][self.anim_frame]
            elif self.state == "normal":
                current_dir = self.dir if self.dir != "NONE" else "DOWN"
                sprite = self.frames[current_dir][self.anim_frame]
            else:
                sprite = None

            # 2. Affichage si un sprite est sélectionné
            if sprite:
                scale_factor = tile_size / max(sprite.get_width(),
                                               sprite.get_height())
                new_width = int(sprite.get_width() * scale_factor)
                new_height = int(sprite.get_height() * scale_factor)
                scaled_sprite = pygame.transform.scale(sprite, (new_width,
                                                                new_height))
                rect = scaled_sprite.get_rect(center=(gx + tile_size // 2,
                                                      gy + tile_size // 2))
                surface.blit(scaled_sprite, rect)
                return
        # GHOST STATE ---------------------------------------------------------
        if self.state != "dead":
            current_color = self.frightened_color if self.state == "scared" \
                else self.color
            pygame.draw.circle(surface, current_color, (cx, cy),
                               tile_size // 2)
            pygame.draw.rect(surface, current_color, (int(gx), cy, tile_size,
                                                      tile_size // 2))

        # GHOST EYES ----------------------------------------------------------
        eye_offset_x = int(tile_size * 0.15) if self.state == "scared" \
            else int(tile_size * 0.2)
        eye_offset_y = int(tile_size * 0.1)

        eye_radius = max(1, int(tile_size * 0.1)) if self.state == "scared" \
            else max(1, int(tile_size * 0.15))
        pupil_radius = max(1, int(tile_size * 0.05))
        look_x, look_y = 0, 0

        if self.state != "scared":
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

        if self.state != "scared":
            pygame.draw.circle(surface, (0, 0, 255),
                               (cx - eye_offset_x + look_x, cy -
                                eye_offset_y + look_y), pupil_radius)
            pygame.draw.circle(surface, (0, 0, 255),
                               (cx + eye_offset_x + look_x, cy -
                                eye_offset_y + look_y), pupil_radius)
