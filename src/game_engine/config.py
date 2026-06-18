"""Central config loader. Reads data/config.json once and caches it."""

from pathlib import Path
from functools import lru_cache
from json import loads
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = ROOT / "data" / "config.json"


# Cache for not reloading game config (optimization)
@lru_cache(maxsize=None)
def get_cfg() -> dict[str, Any]:
    return loads(_CONFIG_PATH.read_text())


def get_gamemode_cfg(mode: str = "original") -> dict[str, Any]:
    """Returns common game constants merged with mode-specific overrides."""
    try:
        cfg = get_cfg()["game"]
        merged = dict(cfg.get("common", {}))
        merged.update(cfg.get(mode, {}))
        return merged
    except Exception as error:
        raise error


def get_highscore_path(mode: str = "original_mode") -> Path:
    "Detects the linked highscore file and returns path / data / filename."
    filename = get_gamemode_cfg(mode).get(
                                         "highscore_filename",
                                         "highscores.json"
                                         )
    return ROOT / "data" / filename
