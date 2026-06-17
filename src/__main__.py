from game_engine.tools.level_generation import Map
from game_engine.core import run

PROGRAM = "Pac-Man"
VERSION = "1.00"
AUTHORS = ["qbourine", "jferone"]


def main():
    for i in range(11):
        if i >= 1:
            map = Map(i)
            map.save(map.create())
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
