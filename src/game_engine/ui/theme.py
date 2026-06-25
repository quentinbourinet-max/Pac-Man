"""Per-mode visual theming (scene background colours)."""

from ..config import get_ui_cfg


def background(mode: str,
               default: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return the scene background colour for the active mode.

    Original mode keeps each scene's own colour; Ironman overrides every
    scene with a single pronounced colour.
    """
    if mode == "ironman":
        return get_ui_cfg()["ironman_bg"]
    return default
