# ====================== SECURIZED PROGRAM ENTRYPOINT ======================= #
# Project   : Pac-Man from 42next
# Authors   : qbourine, jferone
# Language  : Python >3.10

from game_engine.core import run

PROGRAM = "Pac-Man"
VERSION = "1.00"
AUTHORS = ["qbourine", "jferone"]


def main() -> int:                                      # Global errors catcher
    try:
        run()
        return 0

    except KeyboardInterrupt as ki:
        print(f"\n> Program interruption detected :\n  {ki}")
        return 130

    except Exception as e:
        print(f"\nUnexpected error occured:\n  {e}\n")
        return 1


if __name__ == "__main__":
    main()
