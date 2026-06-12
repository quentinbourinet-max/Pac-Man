"""In-game playing level scene."""
from pathlib import Path
import pygame
from ..definitions import Scene

BG_COLOR = (0, 0, 0)
WALL_COLOR = (0, 0, 255)
TEXT_COLOR = (255, 255, 255)
TILE_SIZE = 20
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FONT_PATH = ROOT_DIR / "tools" / "visualisation_tools" / "Minecraftia.ttf"


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

    def handle_events(self, events: list[pygame.event.Event]) -> str | None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "main_menu"
        return None

    def update(self, framesync: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        text_surface = self.level_font.render(f"STAGE  {self.level_id}",
                                              True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.game.width // 2, 10))
        surface.blit(text_surface, text_rect)
        if not self.grid:
            return
        cols = len(self.grid[0])
        rows = len(self.grid)
        offset_x = (self.game.width - (cols * TILE_SIZE)) // 2
        offset_y = (self.game.height - (rows * TILE_SIZE)) // 2

        for r, row in enumerate(self.grid):
            for c, val in enumerate(row):
                x = offset_x + c * TILE_SIZE
                y = offset_y + r * TILE_SIZE
                if val == 15:
                    pygame.draw.rect(surface, ("red"),
                                     (x, y, TILE_SIZE, TILE_SIZE))
                if val & 1:
                    pygame.draw.line(surface, WALL_COLOR, (x, y),
                                     (x + TILE_SIZE, y), 2)
                if val & 2:
                    pygame.draw.line(surface, WALL_COLOR,
                                     (x + TILE_SIZE, y),
                                     (x + TILE_SIZE, y + TILE_SIZE), 2)
                if val & 4:
                    pygame.draw.line(surface, WALL_COLOR,
                                     (x, y + TILE_SIZE),
                                     (x + TILE_SIZE, y + TILE_SIZE), 2)
                if val & 8:
                    pygame.draw.line(surface, WALL_COLOR,
                                     (x, y), (x, y + TILE_SIZE), 2)
