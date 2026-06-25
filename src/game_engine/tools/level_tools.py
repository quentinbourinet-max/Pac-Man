"""Tools and utils for game-levels while playtime."""

import random
from game_engine.config import get_level_seed


class LevelTools:
    """Loads a level grid and exposes wall-aware moves + item placement."""

    def __init__(self, level_id: int) -> None:
        self.DIR_MAP = {
                       "UP": (0, -1),
                       "DOWN": (0, 1),
                       "LEFT": (-1, 0),
                       "RIGHT": (1, 0),
                       "NONE": (0, 0)
                       }
        self.level_id = level_id
        self.grid = self.load_map(level_id)

    def check_level_complete(self, item_grid: list[list[int]]) -> bool:
        """Return True if no pac-gum remains on the map."""
        for row in item_grid:
            for item in row:
                if item > 0:
                    return False
        return True

    def is_move_possible(self, current_col: int,
                         current_row: int, direction: str) -> bool:
        """Check whether moving in a direction is blocked by a wall."""
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

    def is_open_cell(self, col: int, row: int) -> bool:
        """True if (col,row) is in-bounds, not solid, and has at least one
        passable exit (a usable corridor cell, not a dead solid block)."""
        if row < 0 or row >= len(self.grid) or \
                col < 0 or col >= len(self.grid[0]):
            return False
        if self.grid[row][col] == 15:
            return False
        return any(self.is_move_possible(col, row, d)
                   for d in ("UP", "DOWN", "LEFT", "RIGHT"))

    def find_central_open_cell(self) -> list[int]:
        """Return the open corridor cell closest to the maze centre.

        Avoids the old hard-coded [9, 9] spawn: scans outward from the real
        centre of the current grid and returns the first open cell, so
        Pac-Man never starts inside a wall whatever the maze size.
        """
        if not self.grid:
            return [0, 0]
        rows = len(self.grid)
        cols = len(self.grid[0])
        cc, cr = cols // 2, rows // 2
        if self.is_open_cell(cc, cr):
            return [cc, cr]
        max_radius = max(rows, cols)
        for radius in range(1, max_radius + 1):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    if max(abs(dr), abs(dc)) != radius:
                        continue
                    if self.is_open_cell(cc + dc, cr + dr):
                        return [cc + dc, cr + dr]
        return [cc, cr]

    def _corner_super_gum_cells(self, rows: int, cols: int,
                                rng: random.Random) -> set[tuple[int, int]]:
        """Pick one open cell next to each corner to host a super pac-gum.

        Ghost spawns stay in the 4 corners (Q4), so super pac-gums are seeded
        onto an open cell near each corner instead of on the spawn itself.
        """
        corners = [(0, 0), (cols - 1, 0), (0, rows - 1), (cols - 1, rows - 1)]
        chosen: set[tuple[int, int]] = set()
        for cx, cy in corners:
            candidates = []
            for radius in range(0, max(rows, cols)):
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        if max(abs(dr), abs(dc)) != radius:
                            continue
                        nc, nr = cx + dc, cy + dr
                        if (nc, nr) in chosen:
                            continue
                        if (nc, nr) != (cx, cy) and self.is_open_cell(nc, nr):
                            candidates.append((nc, nr))
                if candidates:
                    chosen.add(rng.choice(candidates))
                    break
        return chosen

    def init_item_grid(self,
                       exclude: list[int] | None = None) -> list[list[int]]:
        """Build the item grid (0=empty, 1=pac-gum, 2=super pac-gum).

        Pac-gums fill the accessible corridors (seeded by the level seed so a
        level always looks the same), excluding the 4 corner ghost spawns and
        Pac-Man's start cell. Super pac-gums sit on an open cell near each
        corner (see :meth:`_corner_super_gum_cells`).
        """
        if not self.grid:
            return []
        rows = len(self.grid)
        cols = len(self.grid[0])
        rng = random.Random(get_level_seed(self.level_id))
        super_cells = self._corner_super_gum_cells(rows, cols, rng)
        corners = {(0, 0), (cols - 1, 0), (0, rows - 1), (cols - 1, rows - 1)}
        skip = corners
        if exclude is not None:
            skip = corners | {(exclude[0], exclude[1])}
        item_grid = []
        for r in range(rows):
            item_row = []
            for c in range(cols):
                if (c, r) in super_cells:
                    item_row.append(2)
                elif self.grid[r][c] == 15 or (c, r) in skip \
                        or not self.is_open_cell(c, r):
                    item_row.append(0)
                else:
                    item_row.append(1)
            item_grid.append(item_row)
        return item_grid

    def load_map(self, level_id: int) -> list[list[int]]:
        """Generate this level's maze grid in memory (no disk persistence).

        Level 1 uses a fixed seed (reproducible); subsequent levels are
        randomly generated on each call (subject VI.1)."""
        self.level_id = level_id
        from game_engine.tools.level_generation import generate_grid
        grid = generate_grid(level_id)
        if not grid:
            print(f'Error: could not generate level {level_id}.')
        return grid
