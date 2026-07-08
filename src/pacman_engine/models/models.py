from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import pygame


class PathsConfig(BaseModel):
    config: Path
    highscores: Path
    assets: Path
    font: Optional[Path]
    sprites: Path
    ghosts: Path
    music: Path
    sound_gum: Path
    sound_ghost: Path
    sound_lost: Path

    @model_validator(mode='after')
    def verify_paths_exist(self) -> 'PathsConfig':
        """Vérifie l'existence des fichiers après la création du modèle."""
        root = Path(__file__).resolve().parent.parent.parent.parent
        for field_name, value in self.__dict__.items():
            if isinstance(value, Path):
                resolved_path = value if value.is_absolute() else root / value
                if not resolved_path.exists() and field_name != "highscores":
                    print(f" /!\\ Attention: Le chemin pour '{field_name}' "
                          f"n'existe pas : {resolved_path}")
                    self.__dict__[f"{field_name}"] = None
        return self


class WindowConfig(BaseModel):
    title: str = "Pac-Man"
    width: int = Field(default=800, ge=400, le=2200)
    height: int = Field(default=600, ge=300, le=1080)
    fps: int = Field(default=60, ge=10, le=144)


class LevelsConfig(BaseModel):
    width: int = Field(default=20, ge=10, le=50)
    height: int = Field(default=20, ge=10, le=50)
    dims: List[List[int]] = Field(default_factory=list)
    seed: int = 42

    @field_validator('dims')
    @classmethod
    def validate_level_dimensions(cls, v: List[List[int]]) -> List[List[int]]:
        """Checks that each sub-level in the 'dims' list is at least 10x10."""
        for index, dim in enumerate(v):
            if len(dim) != 2:
                raise ValueError(
                    f"The configuration at index {index} must "
                    "be an array of 2 integers [width, height]."
                )
            if dim[0] < 10 or dim[1] < 10:
                raise ValueError(
                    f"The dimensions of the level at index {index} "
                    f"({dim[0]}x{dim[1]}) cannot be smaller than 10x10."
                )
        return v


class CommonGameConfig(BaseModel):
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
    version: str = "1.0.0"
    default_player_name: str = "PLAYER"


class UIColors(BaseModel):
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
        """Valide que la couleur est un tuple (0-255) ou une
        chaîne reconnue par pygame."""
        try:
            pygame.Color(v)
            if isinstance(v, (tuple, list)):
                if len(v) != 3:
                    raise ValueError("Un tuple de couleur doit contenir 3 "
                                     "valeurs (R, G, B)")
                if not all(0 <= x <= 255 for x in v):
                    raise ValueError("Chaque valeur RGB doit être "
                                     "comprise entre 0 et 255")
            return v
        except (ValueError, TypeError) as e:
            raise ValueError(f"Couleur invalide '{v}': {e}")


class UIConfig(BaseModel):
    colors: UIColors = Field(default_factory=UIColors)


class InstructionsConfig(BaseModel):
    sections: Dict[str, List[str]]


class GameConfigRoot(BaseModel):
    """Modèle racine qui englobe toute la structure du config.json"""
    window: WindowConfig = Field(default_factory=WindowConfig)
    levels: LevelsConfig = Field(default_factory=LevelsConfig)
    game: Dict[str, Any] = Field(default_factory=dict)
    app: AppConfig = Field(default_factory=AppConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    scores: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    paths: PathsConfig | None = None
    instructions: Dict[str, List[str]] = Field(default_factory=dict)
