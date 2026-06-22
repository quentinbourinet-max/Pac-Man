from game_engine.tools.level_tools import LevelTools
import random


class GhostAI:
    def __init__(self) -> None:
        self.oppsing = {"UP": "DOWN",
                        "DOWN": "UP",
                        "LEFT": "RIGHT",
                        "RIGHT": "LEFT"}

    def find_next_move(self, start: list[int], target: list[int],
                       tools: LevelTools, current_dir: str) -> str:
        """
        Exécute un algorithme BFS (Breadth-First Search) pour garantir
        de trouver le chemin le plus court vers la cible
        sans jamais se bloquer.
        """
        start_tuple = tuple(start)
        target_tuple = tuple(target)
        if start_tuple == target_tuple:
            return "NONE"
        queue = [(start_tuple, [])]
        visited = {start_tuple}
        while queue:
            (curr_col, curr_row), path = queue.pop(0)
            if (curr_col, curr_row) == target_tuple:
                return path[0] if path else "NONE"
            is_start = (curr_col, curr_row) == start_tuple
            valid_dirs = []
            for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
                if tools.is_move_possible(curr_col, curr_row, direction):
                    valid_dirs.append(direction)
            for direction in valid_dirs:
                if is_start and len(valid_dirs) > 1 and \
                        direction == self.oppsing.get(current_dir, "NONE"):
                    continue
                dc, dr = tools.DIR_MAP[direction]
                next_tile = (curr_col + dc, curr_row + dr)
                if next_tile not in visited:
                    visited.add(next_tile)
                    queue.append((next_tile, path + [direction]))
        valid_dirs = [d for d in ["UP", "DOWN", "LEFT", "RIGHT"] if
                      tools.is_move_possible(start_tuple[0],
                                             start_tuple[1], d)]
        forward_dirs = [d for d in valid_dirs if
                        d != self.oppsing.get(current_dir, "NONE")]
        if forward_dirs:
            return forward_dirs[0]
        elif valid_dirs:
            return valid_dirs[0]
        return "NONE"

    def get_flee_direction(self, curr_coord: list[int],
                           pacman_coord: list[int], tools: LevelTools,
                           current_dir: str) -> str:
        possible_dirs = []
        for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if tools.is_move_possible(curr_coord[0], curr_coord[1], d):
                if d != self.oppsing.get(current_dir,
                                         "NONE") or current_dir == "NONE":
                    possible_dirs.append(d)
        if not possible_dirs:
            possible_dirs = [d for d in ["UP", "DOWN", "LEFT", "RIGHT"] if
                             tools.is_move_possible(curr_coord[0],
                                                    curr_coord[1], d)]
        if not possible_dirs:
            return "NONE"
        best_dir = possible_dirs[0]
        max_dist = -1
        for d in possible_dirs:
            dc, dr = tools.DIR_MAP[d]
            dist = abs((curr_coord[0] + dc) - pacman_coord[0]) + \
                abs((curr_coord[1] + dr) - pacman_coord[1])
            if dist > max_dist:
                max_dist = dist
                best_dir = d
        return best_dir

    def get_random_move(self, curr_coord: list[int], tools: LevelTools,
                        current_dir: str) -> str:
        """
        Logique pour Inky : choisit une direction valide aléatoirement,
        tout en évitant le demi-tour immédiat.
        """
        valid_dirs = []
        for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if tools.is_move_possible(curr_coord[0], curr_coord[1], d):
                # On évite le demi-tour si possible
                if d != self.oppsing.get(current_dir, "NONE") or \
                        current_dir == "NONE":
                    valid_dirs.append(d)
        # Si on est coincé, on autorise le demi-tour
        if not valid_dirs:
            valid_dirs = [d for d in ["UP", "DOWN", "LEFT", "RIGHT"]
                          if tools.is_move_possible(curr_coord[0],
                                                    curr_coord[1], d)]
        return random.choice(valid_dirs) if valid_dirs else "NONE"
