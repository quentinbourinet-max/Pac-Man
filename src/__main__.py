"""Executable entrypoint at the root of the src folder."""

import sys
from pathlib import Path
from .pacman_engine.core import Game


def main() -> None:
    """Build the game from an optional config path (argv[1]) and run it."""
    config_path = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1]).resolve()
    game = Game(custom_config_path=config_path)
    game.run()


if __name__ == "__main__":
    main()
