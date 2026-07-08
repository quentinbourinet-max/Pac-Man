"""Utility class for parsing configuration and
managing scores without global state."""

import sys
import json
from typing import Any
from pathlib import Path
from json import JSONDecodeError
from pydantic import ValidationError
from ..models.models import (GameConfigRoot, CommonGameConfig, ModeConfig,
                             clamp_scalars)

# Safe ranges for the merged game-mode config, mirroring the ge/le bounds of
# CommonGameConfig / ModeConfig. Values outside these clamp; list-valued keys
# (scatter/chase durations) are checked separately in get_gamemode_cfg.
_GAME_BOUNDS: dict[str, tuple[float, float]] = {
    "speed_multiplier": (0.1, 3.0),
    "ghost_speed": (0.5, 10.0),
    "ghost_frightened_speed": (0.5, 10.0),
    "ghost_dead_speed_mult": (1.0, 5.0),
    "pacman_speed": (0.5, 10.0),
    "collision_radius_ratio": (0.1, 1.5),
    "points_per_gum": (0, 1_000_000),
    "points_per_power_gum": (0, 1_000_000),
    "ghost_points": (0, 1_000_000),
    "lives": (1, 99),
    "level_max_time": (10, 100_000),
    "frightened_duration": (0.0, 100_000.0),
}


class ConfigParser:
    """Handles JSON configuration parsing and score management."""

    def __init__(self, custom_path: Path | None = None) -> None:
        """Resolve the active config path and load it once into a model."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        self.active_path = custom_path if custom_path else (
            root / "data" / "config.json")
        self.config = self._load_config_engine()

    def _load_config_engine(self) -> GameConfigRoot:
        """Loads and validates the configuration file once."""
        if not self.active_path.exists():
            print(f" /!\\ {self.active_path.name} not found.",
                  file=sys.stderr)
            return GameConfigRoot()

        try:
            raw_text = self.active_path.read_text(encoding="utf-8")
            clean_json_text = self.strip_comments(raw_text)
            return GameConfigRoot.model_validate_json(clean_json_text)
        except (JSONDecodeError, ValidationError) as e:
            print(f" /!\\ Configuration error: {e}", file=sys.stderr)
            return GameConfigRoot()

    @staticmethod
    def strip_comments(text: str) -> str:
        """Removes JS-style (//, /* */) and shell-style (#)
        comments from a string."""
        out: list[str] = []
        idx, n = 0, len(text)
        in_string = in_block = in_line = False

        while idx < n:
            char = text[idx]
            nxt = text[idx + 1] if idx + 1 < n else ""

            if in_line:
                if char == "\n":
                    in_line = False
                    out.append(char)
                idx += 1
            elif in_block:
                if char == "*" and nxt == "/":
                    in_block = False
                    idx += 2
                else:
                    idx += 1
            elif in_string:
                out.append(char)
                if char == "\\" and idx + 1 < n:
                    out.append(nxt)
                    idx += 2
                elif char == '"':
                    in_string = False
                    idx += 1
                else:
                    idx += 1
            elif char == '"':
                in_string = True
                out.append(char)
                idx += 1
            elif char == "#" or (char == "/" and nxt == "/"):
                in_line = True
                idx += 2 if char == "/" else 1
            elif char == "/" and nxt == "*":
                in_block = True
                idx += 2
            else:
                out.append(char)
                idx += 1
        return "".join(out)

    def get_ui_cfg(self) -> dict[str, tuple[int, int, int]]:
        """Return the UI colours as a plain dictionary."""
        return self.config.ui.colors.model_dump()

    def get_game_modes(self) -> list[str]:
        """Return the list of configured game modes (excluding 'common')."""
        game_cfg = self.config.game
        modes = [k for k in game_cfg.keys() if k != "common" and
                 isinstance(game_cfg[k], dict)]
        return modes or ["original"]

    def get_gamemode_cfg(self, mode: str) -> dict[str, Any]:
        """Merge the shared 'common' block with the selected mode overrides.

        The merge starts from the model defaults so every consumed key is
        always present, then clamps the numeric values into their safe range
        and repairs invalid duration lists, so an incomplete or out-of-range
        game config cannot crash the game (subject M3/A5).
        """
        defaults: dict[str, Any] = {**CommonGameConfig().model_dump(),
                                    **ModeConfig().model_dump()}
        game_cfg = self.config.game
        common = game_cfg.get("common", {})
        specific = game_cfg.get(mode, {})
        merged: dict[str, Any] = {**defaults, **common, **specific}
        merged = clamp_scalars(merged, _GAME_BOUNDS)
        # clamp_scalars drops any non-numeric override; restore its default.
        for key in _GAME_BOUNDS:
            merged.setdefault(key, defaults[key])
        # Duration lists must be non-empty lists of numbers, else fall back.
        for key in ("scatter_durations", "chase_durations"):
            val = merged.get(key)
            if not isinstance(val, list) or not val or not all(
                    isinstance(x, (int, float)) and not isinstance(x, bool)
                    for x in val):
                merged[key] = defaults[key]
        return merged

    def get_font_path(self) -> Path | None:
        """Return the pixel font path (None if it was missing at load time)."""
        return self.config.paths.font

    def get_music_path(self) -> Path:
        """Return the background music file path."""
        return self.config.paths.music

    def get_sound_gum_path(self) -> Path:
        """Return the "eat gum" sound effect path."""
        return self.config.paths.sound_gum

    def get_sound_ghost_path(self) -> Path:
        """Return the "eat ghost" sound effect path."""
        return self.config.paths.sound_ghost

    def get_sound_lost_path(self) -> Path:
        """Return the "life lost" sound effect path."""
        return self.config.paths.sound_lost

    def get_sprites_path(self) -> Path:
        """Return the Pac-Man sprite folder path."""
        return self.config.paths.sprites

    def get_level_dims(self, level: int) -> tuple[int, int]:
        """Return the (width, height) for a level, falling back to the global
        default dims when the level has no dedicated entry."""
        dims_list = self.config.levels.dims
        index = level - 1
        if 0 <= index < len(dims_list):
            return (dims_list[index][0], dims_list[index][1])
        return (self.config.levels.width, self.config.levels.height)

    def get_level_seed(self, level: int) -> int | None:
        """Return the fixed seed for level 1, or None (random) for the rest."""
        if level == 1:
            return self.config.levels.seed
        return None

    def ensure_highscores_initialized(self, highscores_path: Path) -> None:
        """Creates the highscores file with default structure if missing."""
        if not highscores_path.exists():
            highscores_path.parent.mkdir(parents=True, exist_ok=True)
            initial_scores = self.config.scores or {"original": [],
                                                    "ironman": []}
            with open(highscores_path, "w", encoding="utf-8") as f:
                json.dump(initial_scores, f, indent=4)

    @staticmethod
    def get_scores(highscores_path: Path, mode: str) -> list[dict[str, Any]]:
        """Reads and returns sorted scores from the given path."""
        if not highscores_path.exists():
            return []
        try:
            with open(highscores_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return sorted(data.get(mode, []), key=lambda x: x["score"],
                              reverse=True)[:10]
        except (JSONDecodeError, KeyError):
            return []

    @staticmethod
    def save_score(highscores_path: Path, mode: str,
                   name: str, score: int) -> None:
        """Appends a score and saves the top 10 back to the file."""
        data: dict[str, list[dict[str, Any]]] = {"original": [], "ironman": []}
        if highscores_path.exists():
            try:
                with open(highscores_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except JSONDecodeError:
                pass

        mode_scores = data.get(mode, [])
        mode_scores.append({"name": name, "score": score})
        data[mode] = sorted(mode_scores, key=lambda x: x["score"],
                            reverse=True)[:10]

        with open(highscores_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
