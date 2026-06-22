"""Central config loader: reads a JSON-with-comments file once and caches it.

Comments may use ``#`` or ``//`` (to end of line) or ``/* ... */`` blocks,
full-line or trailing; markers inside JSON strings are preserved (B2). Every
consumed key is type-checked and clamped to a safe range, falling back to the
built-in default with a logged warning, so the config can be edited (even at
peer-review defense) without ever crashing the game (M3, A5).
"""

import sys
from json import loads, JSONDecodeError
from typing import Any
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = ROOT / "data" / "config.json"

_FALLBACK_CONFIG: dict[str, Any] = {
    "window": {
              "title": "Pac-Man",
              "width": 800,
              "height": 600,
              "fps": 60
              },
    "levels": {
               "width": 20,
               "height": 20,
               "dims": [[20, 20], [21, 21], [22, 22], [23, 23], [24, 24],
                        [25, 25], [26, 26], [27, 27], [28, 28], [29, 29]],
               "seed": 42
               },
    "game": {
        "common": {
                  "speed_multiplier": 1.0,
                  "ghost_speed": 3.0,
                  "ghost_frightened_speed": 2.0,
                  "ghost_dead_speed_mult": 2.0,
                  "pacman_speed": 4.0,
                  "collision_radius_ratio": 0.7,
                  "points_per_gum": 10,
                  "points_per_power_gum": 50,
                  "points_1st_ghost": 200
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
                   "speed_multiplier": 1.3,
                   "lives": 1,
                   "level_max_time": 180,
                   "frightened_duration": 5.0,
                   "highscore_filename": "highscores_ironman.json",
                   "scatter_durations": [7, 7, 5, 5],
                   "chase_durations": [30, 30, 30, 999]
                   }
        }
}

_WINDOW_SCHEMA: dict[str, tuple[Any, ...]] = {
    "title": ("str",),
    "width": ("int", 100, 10000),
    "height": ("int", 100, 10000),
    "fps": ("int", 1, 1000),
}
_COMMON_SCHEMA: dict[str, tuple[Any, ...]] = {
    "speed_multiplier": ("float", 0.1, 100.0),
    "ghost_speed": ("float", 0.1, 1000.0),
    "ghost_frightened_speed": ("float", 0.1, 1000.0),
    "ghost_dead_speed_mult": ("float", 1.0, 1000.0),
    "pacman_speed": ("float", 0.1, 1000.0),
    "collision_radius_ratio": ("float", 0.01, 5.0),
}
_MODE_SCHEMA: dict[str, tuple[Any, ...]] = {
    "lives": ("int", 1, 999),
    "level_max_time": ("float", 1.0, 1.0e6),
    "frightened_duration": ("float", 0.0, 1.0e6),
    "highscore_filename": ("str",),
    "scatter_durations": ("list_num",),
    "chase_durations": ("list_num",),
}


class _ConfigStore:
    """Owns the active config path and lazily caches the parsed settings.

    Keeps module state behind a single object instead of a rebindable
    module-level global: the path and its cached parse live together, and
    changing the path simply invalidates the cache.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._cache: dict[str, Any] | None = None

    def set_path(self, path: Path) -> None:
        """Point to a new config file and drop the cached parse."""
        self._path = path
        self._cache = None

    def data(self) -> dict[str, Any]:
        """Return the parsed config (parsed once, then cached)."""
        if self._cache is None:
            self._cache = self._parse()
        return self._cache

    def _parse(self) -> dict[str, Any]:
        """Read + strip comments + merge over defaults; defaults on error."""
        try:
            raw = self._path.read_text(encoding="utf-8")
            parsed = loads(_strip_comments(raw))
            if not isinstance(parsed, dict):
                raise ValueError("config root must be a JSON object")
            return _deep_merge(_FALLBACK_CONFIG, parsed)
        except (OSError, JSONDecodeError, ValueError) as exc:
            print(f"> Config warning: {exc} - using built-in defaults.",
                  file=sys.stderr)
            return dict(_FALLBACK_CONFIG)


_CONFIG = _ConfigStore(_CONFIG_PATH)


def set_config_path(path: Path) -> None:
    """Override the config file path (call before any get_cfg() usage)."""
    _CONFIG.set_path(path)


def _strip_comments(text: str) -> str:
    """Strip ``#`` / ``//`` line comments and ``/* */`` blocks (B2).

    Full-line or trailing. Characters inside double-quoted JSON strings are
    never treated as comment markers, so values like ``"http://x"`` survive.
    """
    out: list[str] = []
    idx, n = 0, len(text)
    in_string = False
    in_block = False
    in_line = False

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
            else:
                if char == '"':
                    in_string = False
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


def _validate_value(key: str, value: Any, default: Any,
                    spec: tuple[Any, ...]) -> Any:
    """Coerce/clamp ``value`` to ``spec``; fall back to ``default`` + log."""
    kind = spec[0]

    if kind == "str":
        if isinstance(value, str):
            return value

    elif kind == "list_num":
        if isinstance(value, list) and \
                all(isinstance(x, (int, float)) and not isinstance(x, bool)
                    for x in value):
            return value

    else:  # numeric
        if not isinstance(value, bool):
            try:
                num = int(value) if kind == "int" else float(value)
            except (TypeError, ValueError):
                num = None
            if num is not None:
                lo = spec[1] if len(spec) > 1 else None
                hi = spec[2] if len(spec) > 2 else None
                clamped = num
                if lo is not None:
                    clamped = max(clamped, lo)
                if hi is not None:
                    clamped = min(clamped, hi)
                if clamped != num:
                    print(f"> Config warning: '{key}'={num} out of range, "
                          f"clamped to {clamped}.", file=sys.stderr)
                return clamped

    print(f"> Config warning: '{key}'={value!r} invalid, "
          f"using default {default!r}.", file=sys.stderr)
    return default


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


def get_cfg() -> dict[str, Any]:
    """Return the parsed, defaults-merged config (cached after first read)."""
    return _CONFIG.data()


def get_window_cfg() -> dict[str, Any]:
    """Return validated window settings (title/width/height/fps)."""
    raw = get_cfg().get("window", {})
    if not isinstance(raw, dict):
        raw = {}
    defaults = _FALLBACK_CONFIG["window"]
    out: dict[str, Any] = dict(defaults)
    for key, spec in _WINDOW_SCHEMA.items():
        out[key] = _validate_value(
                                  key,
                                  raw.get(key, defaults[key]),
                                  defaults[key], spec
                                  )
    return out


def _merge_mode(game: dict[str, Any], mode: str) -> dict[str, Any]:
    """Merge common + selected-mode override (no validation)."""
    merged = dict(game.get("common", {}))
    merged.update(game.get(mode, game.get("original", {})))
    return merged


def get_gamemode_cfg(mode: str = "original") -> dict[str, Any]:
    """Return common+mode constants, each validated and clamped (A5)."""
    try:
        merged = _merge_mode(get_cfg()["game"], mode)
    except Exception as exc:
        print(f"> Config warning: {exc} - using built-in defaults.",
              file=sys.stderr)
        merged = _merge_mode(_FALLBACK_CONFIG["game"], mode)
    defaults = _merge_mode(_FALLBACK_CONFIG["game"], mode)
    validated: dict[str, Any] = {}
    for key, val in merged.items():
        default = defaults.get(key)
        if key in _COMMON_SCHEMA:
            spec: tuple[Any, ...] = _COMMON_SCHEMA[key]
        elif key in _MODE_SCHEMA:
            spec = _MODE_SCHEMA[key]
        elif key.startswith("points_"):
            spec = ("int", 0, None)
            default = default if default is not None else 0
        else:
            validated[key] = val  # unknown key: ignore validation, keep value
            continue
        validated[key] = _validate_value(key, val, default, spec)
    return validated


def get_highscore_path(mode: str = "original") -> Path:
    """Return the highscore JSON file path for the given mode."""
    filename = str(get_gamemode_cfg(mode).get(
                                             "highscore_filename",
                                             "highscores.json"
                                             ))
    return ROOT / "data" / filename


def get_levels_cfg() -> dict[str, Any]:
    """Return the maze-generation block (width/height/seeds) with defaults."""
    try:
        levels = get_cfg().get("levels", {})
        if not isinstance(levels, dict):
            raise ValueError("'levels' must be a JSON object")
        return {**_FALLBACK_CONFIG["levels"], **levels}
    except Exception as exc:
        print(f"> Config warning: {exc} - using built-in defaults.",
              file=sys.stderr)
        return dict(_FALLBACK_CONFIG["levels"])


def get_level_dims(level: int = 1) -> tuple[int, int]:
    """Return the (width, height) for a level (1-based), validated/clamped.

    A per-level ``levels.dims`` list (``[[w, h], ...]``) takes precedence when
    it covers the level; otherwise the global ``levels.width/height`` apply.
    Both are clamped to a safe maze size.
    """
    limits: tuple[Any, ...] = ("int", 5, 200)
    levels = get_levels_cfg()
    width = _validate_value(
                           "levels.width",
                           levels.get("width", 20),
                           20,
                           limits
                           )
    height = _validate_value(
                            "levels.height",
                            levels.get("height", 20),
                            20,
                            limits
                            )
    dims = levels.get("dims")

    if isinstance(dims, list) and 1 <= level <= len(dims):
        entry: list[int] = dims[level - 1]
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            width = _validate_value(
                                   f"levels.dims[{level}].w",
                                   entry[0],
                                   width,
                                   limits
                                   )
            height = _validate_value(
                                    f"levels.dims[{level}].h",
                                    entry[1],
                                    height,
                                    limits
                                    )
    return width, height


def get_level_seed(level: int) -> int | None:
    """Return the maze seed for a level (1-based).

    Level 1 uses the fixed ``levels.seed`` so the first maze is reproducible;
    every later level returns ``None`` so the generator builds a fresh random
    maze each game (subject VI.1).
    """
    if level != 1:
        return None
    try:
        return int(get_levels_cfg().get("seed", 42))
    except (TypeError, ValueError):
        return 42
