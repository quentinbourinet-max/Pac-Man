#!/usr/bin/env python3
"""Entry point: python3 pac-man.py config.json"""
import sys
from pathlib import Path

PROGRAM = "Pac-Man"
VERSION = "1.00"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json", file=sys.stderr)
        return 1

    arg = sys.argv[1]
    if not arg.endswith(".json"):
        print(f"Error: '{arg}' - argument must be a .json file.",
              file=sys.stderr)
        return 1

    config_path = Path(arg)
    if not config_path.exists():
        print(f"Error: config file '{config_path}' not found.",
              file=sys.stderr)
        return 1

    sys.path.insert(0, str(Path(__file__).parent / "src"))

    from game_engine.config import set_config_path
    set_config_path(config_path.resolve())

    from game_engine.core import run
    try:
        run()
        return 0
    except KeyboardInterrupt:
        print(f"\n  > Leaving {PROGRAM} v{VERSION}.\n")
        return 130
    except Exception as exc:
        print(f"\n  Error: {exc}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
