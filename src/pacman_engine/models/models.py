"""Pydantic schemas: the validated, defaults-backed shape of config.json."""

from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import pygame


def clamp_scalars(data: Any, bounds: Dict[str, Tuple[float, float]]) -> Any:
    """Clamp the known numeric keys of a raw dict into their (low, high) range.

    Out-of-range values are clamped to the nearest bound; non-numeric values
    are dropped so the field default applies. Keeps a single bad entry from
    failing validation and discarding the whole config (subject M3/A5).
    """
    if not isinstance(data, dict):
        return data
    out = dict(data)
    for key, (low, high) in bounds.items():
        if key not in out:
            continue
        raw = out[key]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            out.pop(key)
            continue
        out[key] = max(low, min(raw, high))
    return out


class PathsConfig(BaseModel):
    """Filesystem paths: config, highscores, fonts, sprites and audio.

    Every field defaults to the standard ``data/`` layout so a defaults-only
    config (missing or invalid file) still points at real assets and stays
    playable rather than crashing.
    """

    config: Path = Path("data/config.json")
    highscores: Path = Path("data/highscores.json")
    assets: Path = Path("data/assets")
    font: Optional[Path] = Path("data/assets/fonts/Minecraftia.ttf")
    sprites: Path = Path("data/assets/sprites/pacman")
    ghosts: Path = Path("data/assets/sprites/pac_ghosts")
    music: Path = Path("data/assets/music/background_music.ogg")
    sound_gum: Path = Path("data/assets/sfx/eat_gum.ogg")
    sound_ghost: Path = Path("data/assets/sfx/eat_ghost.ogg")
    sound_lost: Path = Path("data/assets/sfx/life_lost.ogg")

    @model_validator(mode='after')
    def verify_paths_exist(self) -> 'PathsConfig':
        """Check every path exists once the model is built; drop the missing
        ones to None (except ``highscores``, created lazily on first run)."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        for field_name, value in self.__dict__.items():
            if isinstance(value, Path):
                resolved_path = value if value.is_absolute() else root / value
                if not resolved_path.exists() and field_name != "highscores":
                    print(f" /!\\ Warning: the path for '{field_name}' "
                          f"does not exist: {resolved_path}")
                    self.__dict__[f"{field_name}"] = None
        return self


class WindowConfig(BaseModel):
    """Window settings: title and clamped width, height and frame rate."""

    title: str = "Pac-Man"
    width: int = Field(default=800, ge=400, le=2200)
    height: int = Field(default=600, ge=300, le=1080)
    fps: int = Field(default=60, ge=10, le=144)

    @model_validator(mode='before')
    @classmethod
    def _clamp(cls, data: Any) -> Any:
        """Clamp out-of-range values instead of raising (M3/A5)."""
        return clamp_scalars(data, {"width": (400, 2200),
                                    "height": (300, 1080),
                                    "fps": (10, 144)})


class LevelsConfig(BaseModel):
    """Maze sizing: fallback width/height, per-level dims and level-1 seed."""

    width: int = Field(default=20, ge=10, le=50)
    height: int = Field(default=20, ge=10, le=50)
    dims: List[List[int]] = Field(default_factory=list)
    seed: int = 42

    @model_validator(mode='before')
    @classmethod
    def _clamp(cls, data: Any) -> Any:
        """Clamp the fallback width/height instead of raising (M3/A5)."""
        return clamp_scalars(data, {"width": (10, 50), "height": (10, 50)})

    @field_validator('dims')
    @classmethod
    def validate_level_dimensions(cls, v: List[List[int]]) -> List[List[int]]:
        """Clamp each 'dims' entry into the valid 10..50 range.

        Malformed entries (not a [width, height] pair) are dropped and any
        out-of-range side is clamped, so an edited config never crashes the
        game (subject M3/A5: clamp invalid values, continue).
        """
        cleaned: List[List[int]] = []
        for dim in v:
            if not isinstance(dim, (list, tuple)) or len(dim) != 2:
                continue
            width = max(10, min(int(dim[0]), 50))
            height = max(10, min(int(dim[1]), 50))
            cleaned.append([width, height])
        return cleaned


class CommonGameConfig(BaseModel):
    """Mode-agnostic tuning: entity speeds, collision ratio and scoring."""

    speed_multiplier: float = Field(default=1.0, ge=0.1, le=3.0)
    ghost_speed: float = Field(default=3.0, ge=0.5, le=10.0)
    ghost_frightened_speed: float = Field(default=2.0, ge=0.5, le=10.0)
    ghost_dead_speed_mult: float = Field(default=2.0, ge=1.0, le=5.0)
    pacman_speed: float = Field(default=4.0, ge=0.5, le=10.0)
    collision_radius_ratio: float = Field(default=0.7, ge=0.1, le=1.5)
    points_per_gum: int = Field(default=10, ge=0)
    points_per_power_gum: int = Field(default=50, ge=0)
    ghost_points: int = Field(default=200, ge=0)


class ModeConfig(BaseModel):
    """Per-mode preset: lives, timer, frightened window and phase durations."""

    lives: int = Field(default=3, ge=1, le=99)
    level_max_time: int = Field(default=300, ge=10)
    frightened_duration: float = Field(default=6.0, ge=0.0)
    scatter_durations: List[float] = Field(default_factory=lambda: [7.0,
                                                                    7.0,
                                                                    5.0,
                                                                    5.0])
    chase_durations: List[float] = Field(default_factory=lambda: [20.0,
                                                                  20.0,
                                                                  20.0,
                                                                  999.0])


class AppConfig(BaseModel):
    """Application metadata: version string and default player name."""

    version: str = "1.0.0"
    default_player_name: str = "PLAYER"


class UIColors(BaseModel):
    """Named UI colours, each an RGB triplet or a pygame-recognised string."""

    bg: Union[Tuple[int, int, int], str] = (10, 10, 30)
    bg_instructions: Union[Tuple[int, int, int], str] = (30, 10, 10)
    bg_game: Union[Tuple[int, int, int], str] = (0, 0, 0)
    title: Union[Tuple[int, int, int], str] = (255, 215, 0)
    text: Union[Tuple[int, int, int], str] = (255, 255, 255)
    hint: Union[Tuple[int, int, int], str] = (150, 150, 150)
    header: Union[Tuple[int, int, int], str] = (255, 203, 71)
    wall: Union[Tuple[int, int, int], str] = (33, 33, 255)
    pacman: Union[Tuple[int, int, int], str] = (255, 255, 0)
    pac_gum: Union[Tuple[int, int, int], str] = (255, 255, 255)
    ghost_frightened: Union[Tuple[int, int, int], str] = (50, 150, 255)
    win: Union[Tuple[int, int, int], str] = (255, 215, 0)
    lose: Union[Tuple[int, int, int], str] = (220, 60, 60)
    ironman_bg: Union[Tuple[int, int, int], str] = (50, 0, 0)
    button_idle: Union[Tuple[int, int, int], str] = (40, 40, 40)
    button_hover: Union[Tuple[int, int, int], str] = (70, 70, 90)
    button_border: Union[Tuple[int, int, int], str] = (255, 215, 0)

    @field_validator('*', mode='before')
    @classmethod
    def validate_color_format(cls, v: Any) -> Any:
        """Validate that a colour is an RGB tuple (0-255) or a string that
        pygame recognises."""
        try:
            pygame.Color(v)
            if isinstance(v, (tuple, list)):
                if len(v) != 3:
                    raise ValueError("A colour tuple must hold 3 values "
                                     "(R, G, B)")
                if not all(0 <= x <= 255 for x in v):
                    raise ValueError("Each RGB value must be in range 0-255")
            return v
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid colour '{v}': {e}")


class UIConfig(BaseModel):
    """UI styling block; currently the named colour palette."""

    colors: UIColors = Field(default_factory=UIColors)


class InstructionsConfig(BaseModel):
    """How-to-play text grouped into named sections of lines."""

    sections: Dict[str, List[str]]


class GameConfigRoot(BaseModel):
    """Root model wrapping the whole config.json structure."""
    window: WindowConfig = Field(default_factory=WindowConfig)
    levels: LevelsConfig = Field(default_factory=LevelsConfig)
    game: Dict[str, Any] = Field(default_factory=dict)
    app: AppConfig = Field(default_factory=AppConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    scores: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    instructions: Dict[str, List[str]] = Field(default_factory=dict)
