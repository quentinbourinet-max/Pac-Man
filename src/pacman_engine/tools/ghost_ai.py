"""Ghost pathfinding helpers: BFS chase, flee and random moves."""

from .level_tools import LevelTools
import random


class GhostAI:
    """Stateless movement policies a ghost queries each step."""

    def __init__(self) -> None:
        """Set up the opposite-direction lookup used to avoid U-turns."""
        self.opposing = {"UP": "DOWN",
                         "DOWN": "UP",
                         "LEFT": "RIGHT",
                         "RIGHT": "LEFT"}

    def find_next_move(self, start: list[int], target: list[int],
                       tools: LevelTools, current_dir: str) -> str:
        """
        Run a BFS (Breadth-First Search) to guarantee finding the shortest
        path to the target without ever getting stuck.
        """
        start_tuple = tuple(start)
        target_tuple = tuple(target)
        if start_tuple == target_tuple:
            return "NONE"
        queue: list[tuple[tuple[int, ...], list[str]]] = [(start_tuple, [])]
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
                        direction == self.opposing.get(current_dir, "NONE"):
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
                        d != self.opposing.get(current_dir, "NONE")]
        if forward_dirs:
            return forward_dirs[0]
        elif valid_dirs:
            return valid_dirs[0]
        return "NONE"

    def get_flee_direction(self, curr_coord: list[int],
                           pacman_coord: list[int], tools: LevelTools,
                           current_dir: str) -> str:
        """Pick the legal move that maximizes distance from Pac-Man (flee
        while frightened), avoiding an immediate U-turn when possible."""
        possible_dirs = []
        for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if tools.is_move_possible(curr_coord[0], curr_coord[1], d):
                if d != self.opposing.get(current_dir,
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
        Inky's logic: pick a valid direction at random,
        while avoiding an immediate U-turn.
        """
        valid_dirs = []
        for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if tools.is_move_possible(curr_coord[0], curr_coord[1], d):
                # Avoid the U-turn when possible
                if d != self.opposing.get(current_dir, "NONE") \
                        or current_dir == "NONE":
                    valid_dirs.append(d)
        # If stuck, allow the U-turn
        if not valid_dirs:
            valid_dirs = [d for d in ["UP", "DOWN", "LEFT", "RIGHT"]
                          if tools.is_move_possible(curr_coord[0],
                                                    curr_coord[1], d)]
        return random.choice(valid_dirs) if valid_dirs else "NONE"
