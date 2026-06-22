"""Per-mode visual theming (scene background colours)."""

# Pronounced, colourful purple used for every scene in Ironman mode.
IRONMAN_BG = (50, 0, 0)


def background(mode: str,
               default: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return the scene background colour for the active mode.

    Original mode keeps each scene's own colour; Ironman overrides every
    scene with a single pronounced purple.
    """
    return IRONMAN_BG if mode == "ironman" else default
