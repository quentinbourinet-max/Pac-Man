"""Executable entrypoint at the root of the src folder."""

import sys
from pathlib import Path
from .pacman_engine.core import Game


def main() -> None:
    config_path = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1]).resolve()
    # On instancie le jeu, mais on ne lance pas asyncio.run ici
    game = Game(custom_config_path=config_path)
    # On retire le asyncio.run() et on appelle directement la méthode asynchrone
    # Note : Puisque vous êtes déjà dans pygbag, on peut appeler la coroutine
    return game.run()


if __name__ == "__main__":
    main()
