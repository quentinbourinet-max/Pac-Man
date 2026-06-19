"""Central config loader: reads a JSON-with-# file once and caches it."""

import sys
from json import loads, JSONDecodeError
from typing import Any
from pathlib import Path
from functools import lru_cache

ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = ROOT / "data" / "config.json"
_config_path: Path = _CONFIG_PATH

# @jferone NOTE: Default fallback if there is a config file problem.
_DEFAULTS: dict[str, Any] = {
    "window": {
              "title": "Pac-Man",
              "width": 800,
              "height": 600,
              "fps": 60
              },

    "game": {
        "common": {
                  "points_per_gum": 10,
                  "points_per_power_gum": 50,
                  "points_1st_ghost": 200,
                  "points_2nd_ghost": 400,
                  "points_3th_ghost": 800,
                  "points_4th_ghost": 1600,
                  "points_per_cherry": 100,
                  "points_per_strawberry": 300,
                  "points_per_orange": 500,
                  "points_per_apple": 700,
                  "points_per_melon": 1000,
                  "points_per_galaxian": 2000,
                  "points_per_bell": 3000,
                  "points_per_key": 5000
                  },
        "original": {
                    "lives": 3,
                    "level_max_time": 300,
                    "frightened_duration": 6.0,
                    "highscore_filename": "highscores.json",
                    "scatter_durations": [7, 7, 5, 5],
                    "chase_durations": [20, 20, 20, 999]
                    },
        "ironman": {
                   "lives": 1,
                   "level_max_time": 180,
                   "frightened_duration": 5.0,
                   "highscore_filename": "highscores_ironman.json",
                   "scatter_durations": [7, 7, 5, 5],
                   "chase_durations": [30, 30, 30, 999]
                   }
        }
}


def set_config_path(path: Path) -> None:
    """Override the config file path (call before any get_cfg() usage)."""
    global _config_path
    _config_path = path
    get_cfg.cache_clear()


def _strip_comments(text: str) -> str:
    """Remove lines whose first non-whitespace character is '#'."""
    return "\n".join(
                    line for line in text.splitlines()
                    if not line.strip().startswith("#")
                    )


def _deep_merge(base: dict[str, Any],
                override: dict[str, Any]) -> dict[str, Any]:
    """Merge override into base recursively; unknown keys are kept as-is."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) \
                         and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


@lru_cache(maxsize=None)
def get_cfg() -> dict[str, Any]:
    """Parse config file (stripping # comments); fall back to defaults."""
    try:
        raw = _config_path.read_text(encoding="utf-8")
        parsed = loads(_strip_comments(raw))
        if not isinstance(parsed, dict):
            raise ValueError("config root must be a JSON object")
        return _deep_merge(_DEFAULTS, parsed)
    except (OSError, JSONDecodeError, ValueError) as exc:
        print(f"> Config warning: {exc} - using built-in defaults.",
              file=sys.stderr)
        return dict(_DEFAULTS)


def get_gamemode_cfg(mode: str = "original") -> dict[str, Any]:
    """Return common constants merged with mode-specific overrides."""
    try:
        cfg = get_cfg()["game"]
        merged = dict(cfg.get("common", {}))
        merged.update(cfg.get(mode, cfg.get("original", {})))
        return merged
    except Exception as exc:
        print(f"> Config warning: {exc} - using built-in defaults.",
              file=sys.stderr)
        game = _DEFAULTS["game"]
        merged = dict(game.get("common", {}))
        merged.update(game.get(mode, game.get("original", {})))
        return merged


def get_highscore_path(mode: str = "original") -> Path:
    """Return the highscore JSON file path for the given mode."""
    filename = get_gamemode_cfg(mode).get("highscore_filename",
                                          "highscores.json")
    return ROOT / "data" / filename
