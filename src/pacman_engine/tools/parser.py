"""Utility class for parsing configuration and
managing scores without global state."""

import sys
import json
from pathlib import Path
from json import JSONDecodeError
from pydantic import ValidationError
from ..models.models import GameConfigRoot


class ConfigParser:
    """Handles JSON configuration parsing and score management."""

    def __init__(self, custom_path: Path | None = None) -> None:
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
            print(f" /!\\ Erreur de configuration: {e}", file=sys.stderr)
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
        """Renvoie les couleurs de l'UI sous forme de dictionnaire."""
        return self.config.ui.colors.model_dump()

    def get_game_modes(self) -> list[str]:
        """Renvoie la liste des modes de jeu configurés."""
        game_cfg = self.config.game
        modes = [k for k in game_cfg.keys() if k != "common" and
                 isinstance(game_cfg[k], dict)]
        return modes or ["original"]

    def get_gamemode_cfg(self, mode: str) -> dict:
        """Fusionne la configuration 'common' avec le mode spécifique."""
        game_cfg = self.config.game
        common = game_cfg.get("common", {})
        specific = game_cfg.get(mode, {})
        merged = common.copy()
        merged.update(specific)
        return merged  # type: ignore[no-any-return]

    def get_font_path(self) -> Path | None:
        assert self.config.paths is not None
        return self.config.paths.font

    def get_music_path(self) -> Path:
        assert self.config.paths is not None
        return self.config.paths.music

    def get_sound_gum_path(self) -> Path:
        assert self.config.paths is not None
        return self.config.paths.sound_gum

    def get_sound_ghost_path(self) -> Path:
        assert self.config.paths is not None
        return self.config.paths.sound_ghost

    def get_sound_lost_path(self) -> Path:
        assert self.config.paths is not None
        return self.config.paths.sound_lost

    def get_sprites_path(self) -> Path:
        assert self.config.paths is not None
        return self.config.paths.sprites

    def get_level_dims(self, level: int) -> tuple[int, int]:
        """Récupère les dimensions basées sur le niveau,
        avec fallback par défaut."""
        dims_list = self.config.levels.dims
        index = level - 1
        if 0 <= index < len(dims_list):
            return (dims_list[index][0], dims_list[index][1])
        return (self.config.levels.width, self.config.levels.height)

    def get_level_seed(self, level: int) -> int | None:
        """Retourne le seed fixe pour le niveau 1,
        et None (aléatoire) pour les autres."""
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
    def get_scores(highscores_path: Path, mode: str) -> list[dict]:
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
        data: dict[str, list[dict]] = {"original": [], "ironman": []}
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
