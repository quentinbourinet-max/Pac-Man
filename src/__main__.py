"""Game Engine entrypoint for Pac-Man."""
from game_engine.tools.level_generation import Map
from game_engine.core import run

PROGRAM = "Pac-Man"
VERSION = "1.00"
AUTHORS = ["qbourine", "jferone"]


def main():
    for level in range(11):  # @jferone NOTE: Do we need a dynamic detector?
        if level >= 1:
            map = Map(level)
            map.save(map.create())
    try:
        run()
        return 0
    except KeyboardInterrupt:
        print("\n> Program interruption detected."
              f"\n  Leaving {PROGRAM} v{VERSION}.\n")
        return 130
    except Exception as e:
        print(f"\nUnexpected error occured:\n  {e}\n")
        return 1


if __name__ == "__main__":
    main()
