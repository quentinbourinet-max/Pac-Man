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

    # Gestion de l'environnement (Exécution standard vs PyInstaller)
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base_dir = Path(__file__).parent

    # On force l'inclusion de la racine du projet dans le sys.path
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))

    # Configuration des arguments pour le sous-programme
    main_script = base_dir / "src" / "__main__.py"
    sys.argv = [str(main_script), str(config_path)]
    
    try:
        # CORRECTION : On utilise run_module au lieu de run_path
        # Cela préserve proprement la hiérarchie de packages de 'src'
        runpy.run_module("src", run_name="__main__")
        return 0
    except Exception as e:
        print(f"Error running game: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())