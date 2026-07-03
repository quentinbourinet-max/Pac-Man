"""Executable entrypoint at the root of the src folder."""

import sys
import asyncio
from pathlib import Path
from game_engine.core import Game


def main() -> None:
    """Consolidated bootstrap function handling CLI
    arguments and execution safety."""
    config_path = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1]).resolve()
    try:
        game = Game(custom_config_path=config_path)
        asyncio.run(game.run())
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        print(f"\n> Error: {exc}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
