#!/usr/bin/env python3
"""CLI entry point: validate the single .json argument and launch the game."""
import sys
from pathlib import Path
import runpy
# if False:
#     import src.__main__


def main() -> int:
    """Validate argv (one existing .json path) then run the game module.

    Return 0 on a clean run, 1 on any misuse or runtime error, so the process
    exits with a clear message and never a raw Python traceback.
    """
    if len(sys.argv) != 2:
        print("Usage: uv run pac-man.py <path_to_config.json>",
              file=sys.stderr)
        return 1
    arg = sys.argv[1]
    if not arg.endswith(".json"):
        print(f"Error: '{arg}' - argument must be a .json file.",
              file=sys.stderr)
        return 1
    config_path = Path(arg).resolve()
    if not config_path.exists():
        print(f"Error: config file '{config_path}' not found.",
              file=sys.stderr)
        return 1
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base_dir = Path(__file__).parent
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    main_script = base_dir / "src" / "__main__.py"
    sys.argv = [str(main_script), str(config_path)]
    try:
        runpy.run_module("src", run_name="__main__")
        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Game stop by the player (Ctrl+C). Goodbye !",
              file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error running game: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
