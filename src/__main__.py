"""Module entrypoint (`python -m`): launch with the default config.

Mazes are generated in memory when each level loads (see
tools.level_generation), so this shell only ignites the engine. The graded
CLI is `pac-man.py`.
"""

import sys
from game_engine.core import launch


if __name__ == "__main__":
    sys.exit(launch())
