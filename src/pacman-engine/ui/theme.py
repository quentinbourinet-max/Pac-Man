"""Per-mode visual theming (scene background colours)."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..tools.parser import ConfigParser


def background(parser: "ConfigParser", mode: str,
               default: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return the scene background colour for the active mode."""
    if mode == "ironman":
        # Utilisation du parser reçu en argument pour obtenir les couleurs
        return parser.get_ui_cfg()["ironman_bg"]
    return default
