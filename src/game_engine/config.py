"""Central config loader: reads a JSON-with-comments file once and caches it.

Comments may use ``#`` or ``//`` (to end of line) or ``/* ... */`` blocks,
full-line or trailing; markers inside JSON strings are preserved (B2). Every
consumed key is type-checked and clamped to a safe range, falling back to the
built-in default with a logged warning, so the config can be edited (even at
peer-review defense) without ever crashing the game (M3, A5).
"""

import re
import sys
import json
from json import loads, dumps, JSONDecodeError
from typing import Any
from pathlib import Path
from .tools.models import FALLBACK_CONFIG as _FALLBACK_CONFIG


class Paths(Path):
    """Single Source of Thruth path redirections using ``Path`` class"""
    ROOT = Path(__file__).resolve().parent.parent.parent
    CONFIG = ROOT / "data" / "config.json"
    HIGHSCORES = ROOT / "data" / "highscores.json"
    ASSETS = ROOT / "data" / "assets"
    FONT = ASSETS / "fonts" / "Minecraftia.ttf"
    SPRITES = ASSETS / "sprites"
    MUSIC = ASSETS / "music" / "background_music.mp3"
    SOUND_GUM = ASSETS / "sfx" / "eat_gum.mp3"
    SOUND_GHOST = ASSETS / "sfx" / "eat_ghost.mp3"
    SOUND_LOST = ASSETS / "sfx" / "life_lost.mp3"


class Schemas:

    WINDOW: dict[str, tuple[Any, ...]] = {
        "title":  ("str",),
        "width":  ("int", 100, 10000),
        "height": ("int", 100, 10000),
        "fps":    ("int", 1, 1000)}

    COMMON: dict[str, tuple[Any, ...]] = {
        "speed_multiplier":       ("float", 0.1, 100.0),
        "ghost_speed":            ("float", 0.1, 1000.0),
        "ghost_frightened_speed": ("float", 0.1, 1000.0),
        "ghost_dead_speed_mult":  ("float", 1.0, 1000.0),
        "pacman_speed":           ("float", 0.1, 1000.0),
        "collision_radius_ratio": ("float", 0.01, 5.0)}

    MODE: dict[str, tuple[Any, ...]] = {
        "lives":               ("int", 1, 999),
        "level_max_time":      ("float", 1.0, 1.0e6),
        "frightened_duration": ("float", 0.0, 1.0e6),

        "scatter_durations":   ("list_num",),
        "chase_durations":     ("list_num",)}


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

    def invalidate(self) -> None:
        """Drop the cached parse (call after any write to the config file)."""
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


_CONFIG = _ConfigStore(Paths.CONFIG)


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

    elif kind == "color":
        if (isinstance(value, list) and len(value) == 3
                and all(isinstance(v, int) and 0 <= v <= 255 for v in value)):
            return tuple(value)

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
    for key, spec in Schemas.WINDOW.items():
        out[key] = _validate_value(key, raw.get(key, defaults[key]),
                                   defaults[key], spec)
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
        if key in Schemas.COMMON:
            spec: tuple[Any, ...] = Schemas.COMMON[key]
        elif key in Schemas.MODE:
            spec = Schemas.MODE[key]
        elif key.startswith("points_"):
            spec = ("int", 0, None)
            default = default if default is not None else 0
        else:
            validated[key] = val
            continue
        validated[key] = _validate_value(key, val, default, spec)
    return validated


def _compact_num_arrays(json_str: str) -> str:
    """Re-collapse multi-line arrays of numbers into a single line.

    json.dumps(indent=N) expands every array; this restores the compact form
    for arrays that contain only numbers (colors, durations, dims pairs…).
    """
    def _join(m: re.Match) -> str:
        nums = re.findall(r"[-\d.]+", m.group(0))
        return "[" + ", ".join(nums) + "]"
    return re.sub(r"\[\n(?:\s+[-\d.]+,?\n)+\s*\]", _join, json_str)


def get_scores(mode: str) -> list[dict]:
    """Charge le top 10 depuis le fichier highscores.json dédié."""
    path = Paths.ROOT / "data" / "highscores.json"
    if not path.exists():
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
            scores = data.get(mode, [])
            return sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    except (json.JSONDecodeError, KeyError):
        return []


def ensure_highscores_initialized() -> None:
    """
    Vérifie si highscores.json existe. 
    S'il est absent, on l'initialise avec les scores présents dans config.json.
    """
    path_highscores = Paths.ROOT / "data" / "highscores.json"
    if not path_highscores.exists():
        cfg_data = get_cfg()
        initial_scores = cfg_data.get("scores", {"original": [],
                                                 "ironman": []})
        with open(path_highscores, "w", encoding="utf-8") as f:
            json.dump(initial_scores, f, indent=4)


def save_score(mode: str, name: str, score: int) -> None:
    """Sauvegarde dans le fichier dédié sans toucher au config.json."""
    path = Paths.ROOT / "data" / "highscores.json"
    data = {}
    if path.exists():
        with open(path, "r") as f:
            data = json.load(f)
    mode_scores = data.get(mode, [])
    mode_scores.append({"name": name, "score": score})
    data[mode] = sorted(mode_scores, key=lambda x: x["score"],
                        reverse=True)[:10]
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


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
    width = _validate_value("levels.width", levels.get("width", 20), 20,
                            limits)
    height = _validate_value("levels.height", levels.get("height", 20), 20,
                             limits)
    dims = levels.get("dims")

    if isinstance(dims, list) and 1 <= level <= len(dims):
        entry: list[int] = dims[level - 1]
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            width = _validate_value(f"levels.dims[{level}].w", entry[0],
                                    width, limits)
            height = _validate_value(f"levels.dims[{level}].h", entry[1],
                                     height, limits)
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


def get_ui_cfg() -> dict[str, Any]:
    """Return UI colors, validated; each value is a (R, G, B) tuple."""
    defaults = _FALLBACK_CONFIG["ui"]["colors"]
    raw = get_cfg().get("ui", {}).get("colors", {})
    if not isinstance(raw, dict):
        raw = {}
    result: dict[str, Any] = {k: tuple(v) for k, v in defaults.items()}
    for key, val in raw.items():
        if key not in defaults:
            continue
        result[key] = _validate_value(f"ui.colors.{key}", val,
                                      tuple(defaults[key]), ("color",))
    return result


def get_app_cfg() -> dict[str, Any]:
    """Return app metadata (version, default_player_name)."""
    defaults = _FALLBACK_CONFIG["app"]
    raw = get_cfg().get("app", {})
    if not isinstance(raw, dict):
        return dict(defaults)
    return {**defaults, **{k: v for k, v in raw.items() if k in defaults
                           and isinstance(v, str)}}
