from pathlib import Path


class LevelTools:

    def __init__(self, level_id):
        self.DIR_MAP = {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0),
            "NONE": (0, 0)
        }
        self.grid = self.load_map(level_id)

    def check_level_complete(self, item_grid) -> bool:
        """Retourne True s'il ne reste aucune pac-gum sur la carte."""
        for row in item_grid:
            for item in row:
                if item > 0:
                    return False
        return True

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
