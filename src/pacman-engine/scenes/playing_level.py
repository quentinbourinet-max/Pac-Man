"""In-game playing level scene."""

import pygame
from typing import TYPE_CHECKING
from game_engine.tools.level_tools import LevelTools
from game_engine.entities.ghost import Ghost
from game_engine.entities.pacman import Pacman
from ..definitions import Scene
from ..ui.theme import background

if TYPE_CHECKING:
    from ..core import Game


class PlayingLevel(Scene):
    """In-game scene: orchestrates entities, scoring, lives, timer and HUD."""

    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.cfg = self.game.parser.get_gamemode_cfg(game.mode)
        try:
            self.level_font = pygame.font.Font(str(
                self.game.parser.get_font_path()), 18)
        except FileNotFoundError:
            print(f" /!\\ Font not found at {self.game.parser.get_font_path()}"
                  ". Falling back to the default font.")
            self.level_font = pygame.font.SysFont("monospace", 18)
        self.level_id = 1
        self.tools = LevelTools(self.game.parser, self.level_id)
        self.pac_spawn = self.tools.find_central_open_cell()
        self.item_grid = self.tools.init_item_grid(exclude=self.pac_spawn)
        speed_mult = float(self.cfg["speed_multiplier"])
        self.pacman_speed = float(self.cfg["pacman_speed"]) * speed_mult
        self.pacman = Pacman(self.pac_spawn, speed=4.0,
                             parser=self.game.parser)
        self.score = 0
        self.lives = int(self.cfg["lives"])
        self.time_limit = float(self.cfg["level_max_time"])
        self.remaining_time = self.time_limit
        self.points_per_gum = int(self.cfg["points_per_gum"])
        self.points_per_power_gum = int(self.cfg["points_per_power_gum"])
        self.points_per_ghost = int(self.cfg["points_1st_ghost"])
        self.frightened_duration = float(self.cfg["frightened_duration"])
        self.level_transition_timer = 0.0
        self.base_ghost_speed = float(self.cfg["ghost_speed"]) * speed_mult
        self.frightened_ghost_speed = speed_mult * float(
            self.cfg["ghost_frightened_speed"])
        self.ghost_dead_speed_mult = float(self.cfg["ghost_dead_speed_mult"])
        self.collision_ratio = float(self.cfg["collision_radius_ratio"])
        self.ghost_speed = self.base_ghost_speed
        self.invincible = False
        self.ghost_spawn_coords = self._corner_spawns()
        ghost_colors = [(255, 0, 0),
                        (255, 182, 193),
                        (0, 255, 255),
                        (255, 165, 0)]
        ghost_names = ["Blinky", "Pinky", "Inky", "Clyde"]
        self.ghosts = [Ghost(self.ghost_spawn_coords[i], ghost_colors[i],
                             ghost_names[i], self.ghost_dead_speed_mult,
                             self.game.parser)
                       for i in range(4)]
        self.frightened_timer = 0.0
        self.scatter_durations = [float(d) for d
                                  in self.cfg["scatter_durations"]]
        self.chase_durations = [float(d) for d
                                in self.cfg["chase_durations"]]
        self.phase = "scatter"
        self.phase_index = 0
        self.phase_timer = 0.0
        self.eat_gum_sound: pygame.mixer.Sound | None = None
        self.eat_ghost_sound: pygame.mixer.Sound | None = None
        self.lost_life_sound: pygame.mixer.Sound | None = None
        try:
            self.eat_gum_sound = pygame.mixer.Sound(str(
                self.game.parser.get_sound_gum_path()))
            self.eat_ghost_sound = pygame.mixer.Sound(str(
                self.game.parser.get_sound_ghost_path()))
            self.lost_life_sound = pygame.mixer.Sound(str(
                self.game.parser.get_sound_lost_path()))
            self.eat_gum_sound.set_volume(0.5)
            self.eat_ghost_sound.set_volume(0.7)
            self.lost_life_sound.set_volume(0.6)
        except pygame.error:
            print(" /!\\ Could not load sound effects."
                  " Silent mode enabled.")
        self.reset_positions()
        self.play_bg_music()
        self.go_to_scene: str | None = None
        self.paused = False
        self.pause_selection = 0

    def play_bg_music(self) -> None:
        try:
            music_path = str(self.game.parser.get_music_path())
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
        except pygame.error:
            print(" /!\\ Could not load the music")

    def _corner_spawns(self) -> list[list[int]]:
        """The four maze corners for the current grid, as [col, row].

        Recomputed per level so ghosts snap to the corners of the actual
        maze (mazes grow level by level), not the first level's corners.
        Order matches the ghost list: top-left, bottom-left, top-right,
        bottom-right.
        """
        rows = len(self.tools.grid)
        cols = len(self.tools.grid[0]) if rows else 1
        return [[0, 0],
                [0, rows - 1],
                [cols - 1, 0],
                [cols - 1, rows - 1]]

    def reset_positions(self) -> None:
        """Reset Pac-Man and the ghosts to their spawn points
        without touching the score or the timer."""
        self.pacman.reset()
        for i, ghost in enumerate(self.ghosts):
            if ghost.state != "dead":
                ghost.coord = list(self.ghost_spawn_coords[i])
                ghost.dir = "NONE"
                ghost.move_timer = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        """Route input: ESC pauses, F1/F2 cheats, arrows/WASD steer Pac-Man."""
        if self.go_to_scene:
            return self.go_to_scene
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.pause_game()
                    return None
                elif event.key == pygame.K_F1:
                    self.invincible = not self.invincible
                elif event.key == pygame.K_F2:
                    self._skip_level()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.pacman.handle_input("UP")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pacman.handle_input("DOWN")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.pacman.handle_input("LEFT")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.pacman.handle_input("RIGHT")
        return None

    def _skip_level(self) -> None:
        """Cheat F2: jump to the next level immediately (eases peer review)."""
        if self.level_transition_timer <= 0:
            self.level_transition_timer = 0.1

    def _reset_phase(self) -> None:
        """Restart the scatter/chase schedule from its first scatter phase."""
        self.phase = "scatter"
        self.phase_index = 0
        self.phase_timer = 0.0

    def _current_phase_duration(self) -> float:
        """Duration (s) of the current phase; inf once the schedule is over.

        A duration >= 999 is treated as infinite (authentic last chase phase).
        """
        table = self.scatter_durations if self.phase == "scatter" \
            else self.chase_durations
        if 0 <= self.phase_index < len(table) \
                and table[self.phase_index] < 999:
            return table[self.phase_index]
        return float("inf")

    def _advance_phase(self, framesync: float) -> None:
        """Tick the scatter/chase clock and flip phase when it elapses.

        The clock is frozen while ghosts are frightened (classic behaviour).
        scatter[i] -> chase[i] -> scatter[i+1] -> ... then the final chase
        phase lasts forever.
        """
        if self.frightened_timer > 0:
            return
        self.phase_timer += framesync
        if self.phase_timer >= self._current_phase_duration():
            self.phase_timer = 0.0
            if self.phase == "scatter":
                self.phase = "chase"
            else:
                self.phase = "scatter"
                self.phase_index += 1

    def _advance_level(self) -> None:
        """Load the next level, recentring Pac-Man on the new maze."""
        self.tools.grid = self.tools.load_map(self.level_id)
        self.pac_spawn = self.tools.find_central_open_cell()
        self.pacman.spawn_coord = list(self.pac_spawn)
        self.item_grid = self.tools.init_item_grid(exclude=self.pac_spawn)
        self.ghost_spawn_coords = self._corner_spawns()
        for ghost, corner in zip(self.ghosts, self.ghost_spawn_coords):
            ghost.spawn_coord = list(corner)
        self.pacman.reset()
        for ghost in self.ghosts:
            ghost.state = "normal"
        self.reset_positions()
        self.remaining_time = self.time_limit
        self.frightened_timer = 0.0
        self.ghost_speed = self.base_ghost_speed
        self._reset_phase()
        self.play_bg_music()

    def update(self, framesync: float) -> None:
        """Advance one frame: timers, entities, collisions, scoring, win."""
        if self.paused or self.go_to_scene:
            return
        if self.level_transition_timer > 0:
            self.level_transition_timer -= framesync
            if self.level_transition_timer <= 0:
                self.level_id += 1
                if self.level_id > 10:
                    self.game.final_score = self.score
                    self.game.final_won = True
                    self.go_to_scene = "end_screen"
                    return
                self._advance_level()
            return
        if self.tools.grid and len(self.tools.grid) > 0 and \
                len(self.tools.grid[0]) > 0:
            cols = len(self.tools.grid[0])
            rows = len(self.tools.grid)
            tile_size = min((self.game.width - 40) // cols,
                            (self.game.height - 80) // rows)
            tile_size = max(10, tile_size)
        else:
            tile_size = 20
        self.remaining_time -= framesync
        if self.remaining_time <= 0:
            # O4: timeout costs one life and resets the level (no instant
            # game-over); game-over only happens once all lives are gone.
            self.lives -= 1
            if self.lives <= 0:
                pygame.mixer.music.stop()
                self.game.final_score = self.score
                self.game.final_won = False
                self.go_to_scene = "end_screen"
                return
            if self.lost_life_sound:
                self.lost_life_sound.play()
            self.reset_positions()
            self.remaining_time = self.time_limit
            self.frightened_timer = 0.0
            self.ghost_speed = self.base_ghost_speed
            self._reset_phase()
            return
        if self.frightened_timer > 0:
            self.frightened_timer -= framesync
            if self.frightened_timer <= 0:
                for ghost in self.ghosts:
                    if ghost.state == "scared":
                        ghost.state = "normal"
                self.ghost_speed = self.base_ghost_speed
        self._advance_phase(framesync)
        for ghost in self.ghosts:
            ghost.update(framesync, self.ghost_speed, self.tools,
                         self.pacman.coord, self.pacman.dir, self.phase)
        moved_tile = self.pacman.update(framesync, self.tools)
        pac_pixel_x, pac_pixel_y = self.pacman.get_pixel_pos(tile_size,
                                                             self.tools)
        for ghost in self.ghosts:
            current_interval = 1.0 / (self.ghost_speed *
                                      self.ghost_dead_speed_mult) if \
                ghost.state == "dead" else 1.0 / self.ghost_speed
            g_progress = ghost.move_timer / current_interval
            g_so_x = -self.tools.DIR_MAP[ghost.dir][0] * \
                (1.0 - g_progress) * tile_size if ghost.dir != "NONE" else 0
            g_so_y = -self.tools.DIR_MAP[ghost.dir][1] * \
                (1.0 - g_progress) * tile_size if ghost.dir != "NONE" else 0
            ghost_pixel_x = ghost.coord[0] * tile_size + g_so_x
            ghost_pixel_y = ghost.coord[1] * tile_size + g_so_y
            distance_sq = (pac_pixel_x - ghost_pixel_x)**2 + \
                (pac_pixel_y - ghost_pixel_y)**2
            if distance_sq < (tile_size * self.collision_ratio)**2:
                if ghost.state == "normal":
                    if self.invincible:
                        continue
                    if self.lost_life_sound:
                        self.lost_life_sound.play()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.mixer.music.stop()
                        self.game.final_score = self.score
                        self.game.final_won = False
                        self.go_to_scene = "end_screen"
                        return
                    else:
                        self.reset_positions()
                        self.frightened_timer = 0.0
                        self.ghost_speed = self.base_ghost_speed
                        self._reset_phase()
                        return
                elif ghost.state == "scared":
                    ghost.state = "dead"
                    self.score += self.points_per_ghost
                    if self.eat_ghost_sound:
                        self.eat_ghost_sound.play()
        if moved_tile:
            c, r = self.pacman.coord[0], self.pacman.coord[1]
            if 0 <= r < len(self.item_grid) and \
                    0 <= c < len(self.item_grid[0]):
                item = self.item_grid[r][c]
                if item > 0:
                    if self.eat_gum_sound:
                        self.eat_gum_sound.play()
                    if item == 1:
                        self.score += self.points_per_gum
                    elif item == 2:
                        self.score += self.points_per_power_gum
                        self.frightened_timer = self.frightened_duration
                        for g in self.ghosts:
                            if g.state == "normal":
                                g.state = "scared"
                        self.ghost_speed = self.frightened_ghost_speed
                    self.item_grid[r][c] = 0
        if self.tools.check_level_complete(self.item_grid):
            self.level_transition_timer = 2.0

    def render(self, surface: pygame.Surface) -> None:
        """Draw the HUD, maze, items, ghosts, Pac-Man and any overlays."""
        colors = self.game.parser.get_ui_cfg()
        surface.fill(background(self.game.parser, self.game.mode,
                                colors["bg_game"]))
        text_surface = self.level_font.render(f"STAGE  {self.level_id}",
                                              True, colors["text"])
        text_rect = text_surface.get_rect(center=(self.game.width // 2, 12))
        surface.blit(text_surface, text_rect)
        score_text = self.level_font.render(f"SCORE: {self.score}",
                                            True, colors["text"])
        surface.blit(score_text, (20, 12))
        minutes = int(self.remaining_time) // 60
        seconds = int(self.remaining_time) % 60
        time_color = colors["lose"] if self.remaining_time < 30 \
            else colors["text"]
        time_text = self.level_font.render(f"TIME: {minutes:02d}:"
                                           f"{seconds:02d}", True, time_color)
        surface.blit(time_text,
                     (self.game.width - time_text.get_width() - 20, 12))
        if self.invincible:
            cheat_text = self.level_font.render("CHEAT ON", True,
                                                (0, 255, 0))
            cheat_rect = cheat_text.get_rect(
                center=(self.game.width // 2, self.game.height - 24))
            surface.blit(cheat_text, cheat_rect)
        lives_text = self.level_font.render("LIVES:", True, colors["text"])
        surface.blit(lives_text, (20, self.game.height - 35))
        if self.pacman.frames:
            life_icon = pygame.transform.scale(self.pacman.frames[2], (20, 20))
            for i in range(self.lives):
                surface.blit(life_icon, (90 + i * 24, self.game.height - 32))
        else:
            for i in range(self.lives):
                pygame.draw.circle(surface, colors["pacman"],
                                   (90 + i * 24, self.game.height - 27), 8)
        if not self.tools.grid:
            return
        cols = len(self.tools.grid[0])
        rows = len(self.tools.grid)
        tile_size = min((self.game.width - 40) // cols,
                        (self.game.height - 80) // rows)
        tile_size = max(10, tile_size)
        offset_x = (self.game.width - (cols * tile_size)) // 2
        offset_y = (self.game.height - (rows * tile_size)) // 2

        for r, row in enumerate(self.tools.grid):
            for c, val in enumerate(row):
                x = offset_x + c * tile_size
                y = offset_y + r * tile_size
                if val == 15:
                    pygame.draw.rect(surface, colors["lose"],
                                     (x, y, tile_size, tile_size))
                if val & 1:
                    pygame.draw.line(surface, colors["wall"], (x, y),
                                     (x + tile_size, y), 2)
                if val & 2:
                    pygame.draw.line(surface, colors["wall"],
                                     (x + tile_size, y),
                                     (x + tile_size, y + tile_size), 2)
                if val & 4:
                    pygame.draw.line(surface, colors["wall"],
                                     (x, y + tile_size),
                                     (x + tile_size, y + tile_size), 2)
                if val & 8:
                    pygame.draw.line(surface, colors["wall"],
                                     (x, y), (x, y + tile_size), 2)
        for r, row in enumerate(self.item_grid):
            for c, item in enumerate(row):
                if item == 0:
                    continue
                x = offset_x + c * tile_size
                y = offset_y + r * tile_size
                center_x = x + tile_size // 2
                center_y = y + tile_size // 2
                if item == 1:
                    pygame.draw.circle(surface, colors["pac_gum"],
                                       (center_x, center_y),
                                       max(1, tile_size // 10))
                elif item == 2:
                    pygame.draw.circle(surface, colors["pac_gum"],
                                       (center_x, center_y),
                                       max(2, tile_size // 5))
        for ghost in self.ghosts:
            ghost.render(surface, offset_x, offset_y, tile_size,
                         self.ghost_speed, self.tools)
        self.pacman.render(surface, offset_x, offset_y, tile_size, self.tools)
        if self.level_transition_timer > 0:
            overlay = pygame.Surface((self.game.width, self.game.height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))
            msg = f"Congratulations! Next level is {self.level_id + 1}"
            text_surface = self.level_font.render(msg, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.game.width // 2,
                                                      self.game.height // 2))
            surface.blit(text_surface, text_rect)
