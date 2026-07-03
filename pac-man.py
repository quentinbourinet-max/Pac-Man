#!/usr/bin/env python3
import sys
from pathlib import Path
import runpy


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: ./pac-man <path_to_config.json>", file=sys.stderr)
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
    base_path = sys._MEIPASS  # type: ignore[attr-defined]
    base_dir = Path(base_path) if getattr(sys,
                                          'frozen',
                                          False) else Path(__file__).parent
    main_script = base_dir / "src" / "__main__.py"
    sys.argv = [str(main_script), str(config_path)]
    try:
        runpy.run_path(str(main_script), run_name="__main__")
        return 0
    except Exception as e:
        print(f"Error running game: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
