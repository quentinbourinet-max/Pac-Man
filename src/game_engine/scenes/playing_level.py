"""In-game playing level scene."""
from pathlib import Path
import pygame
from ..definitions import Scene
import random

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
        self.grid = self.load_map(self.level_id)
        self.item_grid = self.init_item_grid()
        self.pac_anim_timer = 0.0
        self.pac_anim_delay = 0.08
        self.pac_frame_index = 0
        self.pac_frames = []
        self.load_pacman_sprites()
        self.pac_speed = 4.0
        self.move_timer = 0.0
        self.DIR_MAP = {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0),
            "NONE": (0, 0)
        }
        self.score = 0
        self.lives = 3
        self.time_limit = 300.0
        self.remaining_time = self.time_limit
        self.level_transition_timer = 0.0
        self.ghost_speed = 3.0
        self.ghost_spawn_coords = [[0, 0],
                                   [0, len(self.grid) - 1],
                                   [len(self.grid[0]) - 1, 0],
                                   [len(self.grid[0]) - 1, len(self.grid) - 1]]
        self.ghosts = []
        ghost_colors = [
            (255, 0, 0),
            (255, 182, 193),
            (0, 255, 255),
            (255, 165, 0)
        ]
        self.frightened_timer = 0.0
        for i in range(4):
            self.ghosts.append({
                "coord": list(self.ghost_spawn_coords[i]),
                "dir": "NONE",
                "color": ghost_colors[i],
                "move_timer": 0.0,
                "state": "normal",
                "respawn_timer": 0.0
            })
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
        self.pac_coord = [9, 9]
        self.pac_dir = "NONE"
        self.next_dir = "NONE"
        self.last_dir = "RIGHT"
        self.move_timer = 0.0
        for i, ghost in enumerate(self.ghosts):
            if ghost["state"] != "mort":
                ghost["coord"] = list(self.ghost_spawn_coords[i])
                ghost["dir"] = "NONE"
                ghost["move_timer"] = 0.0

    def load_pacman_sprites(self):
        """Charge les 3 images de Pac-Man et prépare la boucle d'animation."""
        try:
            img1 = pygame.image.load(str(SPRITES_DIR
                                         / "1.png")).convert_alpha()
            img2 = pygame.image.load(str(SPRITES_DIR
                                         / "2.png")).convert_alpha()
            img3 = pygame.image.load(str(SPRITES_DIR
                                         / "3.png")).convert_alpha()
            self.pac_frames = [img1, img2, img3, img2]
        except FileNotFoundError:
            print(" /!\\ Images de Pac-Man introuvables. "
                  "Dessin d'un rond jaune par défaut.")
            self.pac_frames = None

    def load_map(self, level_id: int) -> list[list[int]]:
        """Lit le fichier texte généré et le transforme
        en liste de listes d'entiers."""
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        map_path = root_dir / "data" / "levels" / f"level_{level_id}"
        grid = []
        if map_path.exists():
            with open(map_path, "r") as f:
                for line in f:
                    if line.strip():
                        row = [int(x) for x in line.split()]
                        grid.append(row)
        else:
            print(f"Erreur : Le fichier {map_path} est introuvable.")
        return grid

    def init_item_grid(self) -> list[list[int]]:
        """Génère la grille des objets (0=vide, 1=pac-gum, 2=super pac-gum)
        basée sur la structure du labyrinthe."""
        if not self.grid:
            return []
        rows = len(self.grid)
        cols = len(self.grid[0])
        item_grid = []
        for r in range(rows):
            item_row = []
            for c in range(cols):
                val = self.grid[r][c]
                if val == 15:
                    item_row.append(0)
                elif (r == 0 or r == rows - 1) and (c == 0 or c == cols - 1):
                    item_row.append(2)
                else:
                    item_row.append(1)
            item_grid.append(item_row)
        return item_grid

    def is_move_possible(self, current_col: int,
                         current_row: int, direction: str) -> bool:
        """Vérifie si le déplacement vers une direction est bloqué par un mur
        (fin ou plein)."""
        if direction == "NONE":
            return True
        dc, dr = self.DIR_MAP[direction]
        next_col = current_col + dc
        next_row = current_row + dr
        if next_row < 0 or next_row >= len(self.grid) or next_col < 0 \
                or next_col >= len(self.grid[0]):
            return False
        if self.grid[next_row][next_col] == 15:
            return False
        current_val = self.grid[current_row][current_col]
        if direction == "UP" and (current_val & 1):
            return False
        if direction == "RIGHT" and (current_val & 2):
            return False
        if direction == "DOWN" and (current_val & 4):
            return False
        if direction == "LEFT" and (current_val & 8):
            return False
        next_val = self.grid[next_row][next_col]
        if direction == "UP" and (next_val & 4):
            return False
        if direction == "RIGHT" and (next_val & 8):
            return False
        if direction == "DOWN" and (next_val & 1):
            return False
        if direction == "LEFT" and (next_val & 2):
            return False
        return True

    def check_level_complete(self) -> bool:
        """Retourne True s'il ne reste aucune pac-gum sur la carte."""
        for row in self.item_grid:
            for item in row:
                if item > 0:
                    return False
        return True

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        if self.go_to_scene:
            return self.go_to_scene
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return "main_menu"
                elif event.key in (pygame.K_UP, pygame.K_z):
                    self.next_dir = "UP"
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.next_dir = "DOWN"
                elif event.key in (pygame.K_LEFT, pygame.K_q):
                    self.next_dir = "LEFT"
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.next_dir = "RIGHT"
        return None

    def update(self, framesync: float) -> None:
        if self.level_transition_timer > 0:
            self.level_transition_timer -= framesync
            if self.level_transition_timer <= 0:
                self.level_id += 1
                if self.level_id > 10:
                    self.go_to_scene = "main_menu"
                    return
                self.grid = self.load_map(self.level_id)
                self.item_grid = self.init_item_grid()
                self.pac_coord = [9, 9]
                for ghost in self.ghosts:
                    ghost["state"] = "normal"
                self.reset_positions()
                self.remaining_time = self.time_limit
                self.frightened_timer = 0.0
                self.play_bg_music()
            return
        if self.grid and len(self.grid) > 0 and len(self.grid[0]) > 0:
            cols = len(self.grid[0])
            rows = len(self.grid)
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
                    if ghost["state"] == "appeure":
                        ghost["state"] = "normal"
                        self.ghost_speed = 3.0
        ghost_interval = 1.0 / self.ghost_speed
        for ghost in self.ghosts:
            if ghost["state"] == "mort":
                continue
            ghost["move_timer"] += framesync
            if ghost["move_timer"] >= ghost_interval:
                ghost["move_timer"] -= ghost_interval
                possible_dirs = []
                for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
                    if self.is_move_possible(ghost["coord"][0],
                                             ghost["coord"][1], d):
                        opposing = {
                            "UP": "DOWN",
                            "DOWN": "UP",
                            "LEFT": "RIGHT",
                            "RIGHT": "LEFT"}
                        if d != opposing.get(ghost["dir"], "NONE") or \
                                ghost["dir"] == "NONE":
                            possible_dirs.append(d)
                if not possible_dirs:
                    possible_dirs = [
                        d for
                        d in ["UP", "DOWN", "LEFT", "RIGHT"]
                        if self.is_move_possible(ghost["coord"][0],
                                                 ghost["coord"][1], d)
                        ]
                current_still_possible = self.is_move_possible(
                    ghost["coord"][0], ghost["coord"][1], ghost["dir"]
                    )
                if not current_still_possible or \
                    (len(possible_dirs) > 1 and random.random() < 0.3) or \
                        ghost["dir"] == "NONE":
                    if possible_dirs:
                        ghost["dir"] = random.choice(possible_dirs)
                    else:
                        ghost["dir"] = "NONE"
                if ghost["dir"] != "NONE":
                    dc, dr = self.DIR_MAP[ghost["dir"]]
                    ghost["coord"][0] += dc
                    ghost["coord"][1] += dr
        p_interval = 1.0 / self.pac_speed
        p_progress = self.move_timer / p_interval
        p_so_x = -self.DIR_MAP[self.pac_dir][0] * (1.0 - p_progress) * \
            tile_size if self.pac_dir != "NONE" else 0
        p_so_y = -self.DIR_MAP[self.pac_dir][1] * (1.0 - p_progress) * \
            tile_size if self.pac_dir != "NONE" else 0
        pac_pixel_x = self.pac_coord[0] * tile_size + p_so_x
        pac_pixel_y = self.pac_coord[1] * tile_size + p_so_y

        for i, ghost in enumerate(self.ghosts):
            if ghost["state"] == "mort":
                ghost["respawn_timer"] -= framesync
                if ghost["respawn_timer"] <= 0:
                    ghost["state"] = "normal"
                    ghost["coord"] = list(self.ghost_spawn_coords[i])
                    ghost["dir"] = "NONE"
                    ghost["move_timer"] = 0.0
                else:
                    continue
            g_progress = ghost["move_timer"] / ghost_interval
            g_so_x = -self.DIR_MAP[ghost["dir"]][0] * (1.0 - g_progress) * \
                tile_size if ghost["dir"] != "NONE" else 0
            g_so_y = -self.DIR_MAP[ghost["dir"]][1] * (1.0 - g_progress) * \
                tile_size if ghost["dir"] != "NONE" else 0
            ghost_pixel_x = ghost["coord"][0] * tile_size + g_so_x
            ghost_pixel_y = ghost["coord"][1] * tile_size + g_so_y
            distance_sq = (pac_pixel_x - ghost_pixel_x)**2 + \
                (pac_pixel_y - ghost_pixel_y)**2
            if distance_sq < (tile_size * 0.7)**2:
                if ghost["state"] == "normal":
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
                elif ghost["state"] == "appeure":
                    ghost["state"] = "mort"
                    ghost["respawn_timer"] = 10.0
                    self.score += 200
                    if self.eat_ghost_sound:
                        self.eat_ghost_sound.play()
        self.pac_anim_timer += framesync
        if self.pac_anim_timer >= self.pac_anim_delay:
            self.pac_anim_timer = 0.0
            if self.pac_dir != "NONE":
                self.pac_frame_index = (self.pac_frame_index + 1) % 4
        self.move_timer += framesync
        interval = 1.0 / self.pac_speed
        if self.move_timer >= interval:
            self.move_timer -= interval
            if self.is_move_possible(self.pac_coord[0], self.pac_coord[1],
                                     self.next_dir):
                self.pac_dir = self.next_dir
            if self.is_move_possible(self.pac_coord[0], self.pac_coord[1],
                                     self.pac_dir):
                dc, dr = self.DIR_MAP[self.pac_dir]
                self.pac_coord[0] += dc
                self.pac_coord[1] += dr
                self.last_dir = self.pac_dir
            else:
                self.pac_dir = "NONE"
            c, r = self.pac_coord[0], self.pac_coord[1]
            if 0 <= r < len(self.item_grid) \
                    and 0 <= c < len(self.item_grid[0]):
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
                            if g["state"] == "normal":
                                g["state"] = "appeure"
                                self.ghost_speed = 2.0
                    self.item_grid[r][c] = 0
        if self.check_level_complete():
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
        if self.pac_frames:
            life_icon = pygame.transform.scale(self.pac_frames[2], (16, 16))
            for i in range(self.lives):
                surface.blit(life_icon, (80 + i * 20, self.game.height - 35))
        else:
            for i in range(self.lives):
                pygame.draw.circle(surface, PACMAN_COLOR,
                                   (90 + i * 20, self.game.height - 27), 8)
        if not self.grid:
            return
        cols = len(self.grid[0])
        rows = len(self.grid)
        tile_size = min((self.game.width - 40) // cols,
                        (self.game.height - 80) // rows)
        tile_size = max(10, tile_size)
        offset_x = (self.game.width - (cols * tile_size)) // 2
        offset_y = (self.game.height - (rows * tile_size)) // 2

        for r, row in enumerate(self.grid):
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
        ghost_interval = 1.0 / self.ghost_speed
        for ghost in self.ghosts:
            if ghost["state"] == "mort":
                continue
            g_progress = ghost["move_timer"] / ghost_interval
            g_so_x = -self.DIR_MAP[ghost["dir"]][0] * (1.0 - g_progress) * \
                tile_size if ghost["dir"] != "NONE" else 0
            g_so_y = -self.DIR_MAP[ghost["dir"]][1] * (1.0 - g_progress) * \
                tile_size if ghost["dir"] != "NONE" else 0
            gx = offset_x + ghost["coord"][0] * tile_size + g_so_x
            gy = offset_y + ghost["coord"][1] * tile_size + g_so_y
            cx, cy = int(gx + tile_size // 2), int(gy + tile_size // 2)
            current_color = FRIGHTENED_COLOR if ghost["state"] == "appeure" \
                else ghost["color"]
            pygame.draw.circle(surface, current_color, (cx, cy),
                               tile_size // 2)
            pygame.draw.rect(surface, current_color, (gx, cy,
                                                      tile_size,
                                                      tile_size // 2))
            eye_offset_x = int(tile_size * 0.15) \
                if ghost["state"] == "appeure" else int(tile_size * 0.2)
            eye_offset_y = int(tile_size * 0.1)
            eye_radius = max(1, int(tile_size * 0.1)) \
                if ghost["state"] == "appeure" else max(1,
                                                        int(tile_size * 0.15))
            if ghost["state"] == "appeure":
                pygame.draw.circle(surface, (255, 255, 255),
                                   (cx - eye_offset_x, cy - eye_offset_y),
                                   eye_radius)
                pygame.draw.circle(surface, (255, 255, 255),
                                   (cx + eye_offset_x, cy - eye_offset_y),
                                   eye_radius)
            else:
                pygame.draw.circle(surface, (255, 255, 255),
                                   (cx - eye_offset_x, cy - eye_offset_y),
                                   eye_radius)
                pygame.draw.circle(surface, (255, 255, 255),
                                   (cx + eye_offset_x, cy - eye_offset_y),
                                   eye_radius)
                pygame.draw.circle(surface, (0, 0, 255),
                                   (cx - eye_offset_x, cy - eye_offset_y),
                                   max(1, int(tile_size * 0.05)))
                pygame.draw.circle(surface, (0, 0, 255),
                                   (cx + eye_offset_x, cy - eye_offset_y),
                                   max(1, int(tile_size * 0.05)))
        interval = 1.0 / self.pac_speed
        progress = self.move_timer / interval
        smooth_offset_x = 0
        smooth_offset_y = 0
        if self.pac_dir != "NONE":
            dc, dr = self.DIR_MAP[self.pac_dir]
            smooth_offset_x = -dc * (1.0 - progress) * tile_size
            smooth_offset_y = -dr * (1.0 - progress) * tile_size
        pac_pixel_x = offset_x + self.pac_coord[0] * tile_size \
            + smooth_offset_x
        pac_pixel_y = offset_y + self.pac_coord[1] * tile_size + \
            smooth_offset_y
        if self.pac_frames:
            current_image = self.pac_frames[self.pac_frame_index]
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
            rect = transformed_image.get_rect(center=(pac_pixel_x
                                                      + tile_size // 2,
                                                      pac_pixel_y
                                                      + tile_size // 2))
            surface.blit(transformed_image, rect)
        else:
            pygame.draw.circle(surface, PACMAN_COLOR,
                               (int(pac_pixel_x + tile_size // 2),
                                int(pac_pixel_y + tile_size // 2)),
                               tile_size // 2)
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
