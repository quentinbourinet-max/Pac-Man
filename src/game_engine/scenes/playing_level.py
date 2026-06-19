"""In-game playing level scene."""
from pathlib import Path
from game_engine.tools.level_tools import LevelTools
from game_engine.entities.ghost import Ghost
from game_engine.entities.pacman import Pacman
import pygame
from ..definitions import Scene

BG_COLOR = (0, 0, 0)
WALL_COLOR = (33, 33, 255)
TEXT_COLOR = (255, 255, 255)
PAC_GUM_COLOR = (255, 255, 255)
PACMAN_COLOR = (255, 255, 0)
FRIGHTENED_COLOR = (50, 150, 255)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"
SPRITES_DIR = ROOT_DIR / "tools" / "visualisation_tools" / "pac-man_sprites"
MUSIC_PATH = ROOT_DIR / "tools" / "visualisation_tools" \
    / "background_music.mp3"
SOUND_GUM_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "eat_gum.mp3"
SOUND_GHOST_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "eat_ghost.mp3"
SOUND_LOST_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "life_lost.mp3"


class PlayingLevel(Scene):
    def __init__(self, game) -> None:
        super().__init__(game)
        try:
            self.level_font = pygame.font.Font(str(FONT_PATH), 18)
        except FileNotFoundError:
            print(f" /!\\ Police introuvable à {FONT_PATH}."
                  " Repli sur la police par défaut.")
            self.level_font = pygame.font.SysFont("monospace", 18)
        self.level_id = 1
        self.tools = LevelTools(self.level_id)
        self.item_grid = self.tools.init_item_grid()
        self.pacman = Pacman()
        self.score = 0
        self.lives = 3
        self.time_limit = 300.0
        self.remaining_time = self.time_limit
        self.level_transition_timer = 0.0
        self.ghost_speed = 3.0
        self.ghost_spawn_coords = [[0, 0],
                                   [0, len(self.tools.grid) - 1],
                                   [len(self.tools.grid[0]) - 1, 0],
                                   [len(self.tools.grid[0]) - 1,
                                    len(self.tools.grid) - 1]]
        ghost_colors = [(255, 0, 0),
                        (255, 182, 193),
                        (0, 255, 255),
                        (255, 165, 0)]
        ghost_names = ["Blinky", "Pinky", "Inky", "Clyde"]
        self.ghosts = [Ghost(self.ghost_spawn_coords[i], ghost_colors[i],
                             ghost_names[i]) for i in range(4)]
        self.frightened_timer = 0.0
        try:
            self.eat_gum_sound = pygame.mixer.Sound(str(SOUND_GUM_PATH))
            self.eat_ghost_sound = pygame.mixer.Sound(str(SOUND_GHOST_PATH))
            self.lost_life_sound = pygame.mixer.Sound(str(SOUND_LOST_PATH))
            self.eat_gum_sound.set_volume(0.5)
            self.eat_ghost_sound.set_volume(0.7)
            self.lost_life_sound.set_volume(0.6)
        except pygame.error:
            print(" /!\\ Impossible de charger les effets sonores."
                  "Mode silencieux activé.")
            self.eat_gum_sound = None
            self.eat_ghost_sound = None
        self.reset_positions()
        self.play_bg_music()
        self.go_to_scene = None
        self.paused = False
        self.pause_selection = 0

    def play_bg_music(self) -> None:
        """Charge et lance la musique de fond en boucle depuis le début."""
        try:
            pygame.mixer.music.load(str(MUSIC_PATH))
            pygame.mixer.music.play(-1)
        except pygame.error:
            print(" /!\\ Impossible de charger la musique "
                  f"à l'emplacement : {MUSIC_PATH}")

    def reset_positions(self) -> None:
        """Remet Pac-Man et les fantômes à leurs points de départ
        sans toucher au score ni au timer."""
        self.pacman.reset()
        for i, ghost in enumerate(self.ghosts):
            if ghost.state != "mort":
                ghost.coord = list(self.ghost_spawn_coords[i])
                ghost.dir = "NONE"
                ghost.move_timer = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        if self.go_to_scene:
            return self.go_to_scene
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.pause_game()
                    return None
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.pacman.handle_input("UP")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pacman.handle_input("DOWN")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.pacman.handle_input("LEFT")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.pacman.handle_input("RIGHT")
        return None

    def update(self, framesync: float) -> None:
        if self.paused:
            return
        if self.level_transition_timer > 0:
            self.level_transition_timer -= framesync
            if self.level_transition_timer <= 0:
                self.level_id += 1
                if self.level_id > 10:
                    self.go_to_scene = "main_menu"
                    return
                self.tools.grid = self.tools.load_map(self.level_id)
                self.item_grid = self.tools.init_item_grid()
                self.pacman.reset()
                for ghost in self.ghosts:
                    ghost.state = "normal"
                self.reset_positions()
                self.remaining_time = self.time_limit
                self.frightened_timer = 0.0
                self.play_bg_music()
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
            self.go_to_scene = "main_menu"
            return
        if self.frightened_timer > 0:
            self.frightened_timer -= framesync
            if self.frightened_timer <= 0:
                for ghost in self.ghosts:
                    if ghost.state == "appeure":
                        ghost.state = "normal"
                        self.ghost_speed = 3.0
        for ghost in self.ghosts:
            ghost.update(framesync, self.ghost_speed, self.tools,
                         self.pacman.coord, self.pacman.dir)
        moved_tile = self.pacman.update(framesync, self.tools)
        pac_pixel_x, pac_pixel_y = self.pacman.get_pixel_pos(tile_size,
                                                             self.tools)
        for ghost in self.ghosts:
            current_interval = 1.0 / (self.ghost_speed * 2.0) if \
                ghost.state == "mort" else 1.0 / self.ghost_speed
            g_progress = ghost.move_timer / current_interval
            g_so_x = -self.tools.DIR_MAP[ghost.dir][0] * \
                (1.0 - g_progress) * tile_size if ghost.dir != "NONE" else 0
            g_so_y = -self.tools.DIR_MAP[ghost.dir][1] * \
                (1.0 - g_progress) * tile_size if ghost.dir != "NONE" else 0
            ghost_pixel_x = ghost.coord[0] * tile_size + g_so_x
            ghost_pixel_y = ghost.coord[1] * tile_size + g_so_y
            distance_sq = (pac_pixel_x - ghost_pixel_x)**2 + \
                (pac_pixel_y - ghost_pixel_y)**2
            if distance_sq < (tile_size * 0.7)**2:
                if ghost.state == "normal":
                    if self.lost_life_sound:
                        self.lost_life_sound.play()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.mixer.music.stop()
                        self.go_to_scene = "main_menu"
                        return
                    else:
                        self.reset_positions()
                        return
                elif ghost.state == "appeure":
                    ghost.state = "mort"
                    self.score += 200
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
                        self.score += 10
                    elif item == 2:
                        self.score += 50
                        self.frightened_timer = 30.0
                        for g in self.ghosts:
                            if g.state == "normal":
                                g.state = "appeure"
                        self.ghost_speed = 2.0
                    self.item_grid[r][c] = 0
        if self.tools.check_level_complete(self.item_grid):
            self.level_transition_timer = 2.0

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        text_surface = self.level_font.render(f"STAGE  {self.level_id}",
                                              True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.game.width // 2, 12))
        surface.blit(text_surface, text_rect)
        score_text = self.level_font.render(f"SCORE: {self.score}",
                                            True, TEXT_COLOR)
        surface.blit(score_text, (20, 12))
        minutes = int(self.remaining_time) // 60
        seconds = int(self.remaining_time) % 60
        color = (255, 0, 0) if self.remaining_time < 30 else TEXT_COLOR
        time_text = self.level_font.render(f"TEMPS: {minutes:02d}:"
                                           f"{seconds:02d}", True, color)
        surface.blit(time_text,
                     (self.game.width - time_text.get_width() - 20, 12))
        lives_text = self.level_font.render("VIES:", True, TEXT_COLOR)
        surface.blit(lives_text, (20, self.game.height - 35))
        if self.pacman.frames:
            life_icon = pygame.transform.scale(self.pacman.frames[2], (16, 16))
            for i in range(self.lives):
                surface.blit(life_icon, (80 + i * 20, self.game.height - 35))
        else:
            for i in range(self.lives):
                pygame.draw.circle(surface, PACMAN_COLOR,
                                   (90 + i * 20, self.game.height - 27), 8)
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
                    pygame.draw.rect(surface, ("red"),
                                     (x, y, tile_size, tile_size))
                if val & 1:
                    pygame.draw.line(surface, WALL_COLOR, (x, y),
                                     (x + tile_size, y), 2)
                if val & 2:
                    pygame.draw.line(surface, WALL_COLOR,
                                     (x + tile_size, y),
                                     (x + tile_size, y + tile_size), 2)
                if val & 4:
                    pygame.draw.line(surface, WALL_COLOR,
                                     (x, y + tile_size),
                                     (x + tile_size, y + tile_size), 2)
                if val & 8:
                    pygame.draw.line(surface, WALL_COLOR,
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
                    pygame.draw.circle(surface, PAC_GUM_COLOR,
                                       (center_x, center_y),
                                       max(1, tile_size // 10))
                elif item == 2:
                    pygame.draw.circle(surface, PAC_GUM_COLOR,
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
            msg = f"Congratulation! Now level {self.level_id + 1}"
            text_surface = self.level_font.render(msg, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.game.width // 2,
                                                      self.game.height // 2))
            surface.blit(text_surface, text_rect)
