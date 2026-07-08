*This project has been created as part of the 42 curriculum by qbourine, jferone.*

# Pac-Man

## Description

A complete, playable Pac-Man game written in Python with pygame. The player
moves through generated mazes, eats pac-gums, avoids four ghosts, and clears
ten levels of increasing size. Eating a super pac-gum turns the ghosts edible
for a short time. The game keeps a persistent top-ten highscore board and
offers two game modes (Original and Ironman).

The game flow is: Main Menu, then a level run, then a Game Over or Victory
screen with name entry, then back to the Main Menu.

## Instructions

Requirements: Python 3.10 or later. The maze generator package (the assigned
A-Maze-ing wheel) ships at the repository root as `mazegenerator-*.whl`.

Install the dependencies:

```
make install
```

This installs the maze generator wheel found at the repository root plus
pygame. To install lint tooling as well:

```
make install-lint
```

Run the game with the bundled configuration:

```
make run
```

Or run it directly, passing exactly one `.json` configuration file:

```
python3 pac-man.py data/config.json
```

Other Makefile rules:

- `make debug` runs the game under `pdb`.
- `make clean` removes `__pycache__`, `.mypy_cache` and temporary files.
- `make lint` runs `flake8` and `mypy`.
- `make lint-strict` runs `flake8` and `mypy --strict`.

Controls:

- Move: arrow keys, WASD or ZQSD.
- Pause and resume: ESC (the pause screen also has Resume and Main Menu).
- Validate the name at the end screen: ENTER.
- Cheat, toggle invincibility: F1.
- Cheat, skip to the next level: F2.

Main menu entries: PLAY, MODE (cycles between Original and Ironman), SCORES,
HOW TO PLAY, QUIT.

## Resources

- Python 3.10+ and the standard library.
- pygame for the window, input, rendering, audio and timing.
- The externally assigned A-Maze-ing package (`mazegenerator`), used as-is and
  reinstalled at peer review. It is never modified by this project.
- Fonts, sprites and sound files under `tools/visualisation_tools`.

AI usage: this project was developed with the help of an AI coding assistant
(Claude). The assistant was used for code review, refactoring, docstring and
documentation writing, lint cleanup and test scaffolding. Every design
decision and every committed line was reviewed and validated by the authors.

## Configuration

The game reads a single JSON configuration file given on the command line.
Comment lines and trailing comments are allowed with `#`, `//` and `/* */`,
and markers inside string values are preserved. Unknown keys are ignored.
Every value the game consumes is type checked and clamped to a safe range; an
invalid or missing value falls back to a built-in default with a logged
warning, so editing the file can never crash the game.

Top level blocks:

- `window`: `title`, `width`, `height`, `fps`.
- `levels`: `width`, `height`, an optional per-level `dims` list of
  `[width, height]` pairs, and `seed` (the fixed seed of the first level).
- `game.common`: scoring (`points_per_gum`, `points_per_power_gum`,
  `ghost_points`) and tuning (`speed_multiplier`, `ghost_speed`,
  `ghost_frightened_speed`, `ghost_dead_speed_mult`, `pacman_speed`,
  `collision_radius_ratio`).
- `game.<mode>`: per-mode values (`lives`, `level_max_time`,
  `frightened_duration`, `highscore_filename`, `scatter_durations`,
  `chase_durations`). The shipped modes are `original` and `ironman`
  (Ironman: one life, shorter timer, faster via `speed_multiplier`).

The active mode is chosen from the main menu. Common values are merged with
the selected mode, so a mode only overrides what it needs.

## Highscore

Highscores are stored as a JSON file on disk, one file per mode (for example
`data/highscores.json` and `data/highscores_ironman.json`). The board keeps
the top ten entries, each with a name and a score. Names are at most ten
characters, alphanumeric and spaces only. Scores are non-negative integers.
The board is loaded at game start and saved at game end. A missing or corrupt
file is tolerated: the game starts from an empty board and logs a warning
rather than crashing.

The player enters a name on both the Game Over and the Victory screen, and the
top ten is shown from the SCORES entry of the main menu.

## Maze Generation

Mazes come from the externally assigned A-Maze-ing package (`mazegenerator`).
The project does not write its own generator and does not modify the package.
All calls go through a single adapter, `MazeAdapter`, so the loader adapts to
the package interface rather than the opposite, and a future package version
only affects that one class.

Mazes are generated with `perfect=False`, which produces braided corridors
with loops suitable for Pac-Man. The first level uses a fixed seed so its maze
is reproducible; every subsequent level is generated randomly on each playthrough
(as the subject requires). Mazes are built in memory each time a level loads, so
nothing is persisted between runs; a generator failure is handled cleanly without
crashing the game.

Each cell is stored as a wall bitmask: bit 1 is the top wall, bit 2 the right
wall, bit 4 the bottom wall, bit 8 the left wall, and the value 15 marks a
solid cell. Pac-Man starts on the open cell closest to the real center of the
current maze, the four ghosts spawn in the corners, and the super pac-gums are
placed on an open cell next to each corner.

## Implementation

The game runs on a small scene engine. One scene is active per frame and
follows a `handle_events`, `update`, `render` cycle. Scenes request
transitions by name through a registry held by the engine. Pausing keeps the
play scene alive underneath a pause screen.

Pac-Man moves cell by cell with a buffered next direction and smooth pixel
interpolation. The four ghosts each run a state machine (normal, scared,
dead-eyes) over breadth-first pathfinding. In chase phase each ghost uses its
own target (Blinky goes straight for Pac-Man, Pinky aims four cells ahead,
Clyde chases when far and retreats to its corner when close). A global
scatter and chase clock, driven by the configured durations and frozen while
the ghosts are frightened, sends the ghosts to their home corner during
scatter. Inky always wanders randomly, which is a deliberate design choice.
A frightened ghost flees, and an eaten ghost returns to its spawn as eyes
before becoming normal again.

The configuration loader, the highscore store and the maze loader are all
written to tolerate missing files and bad input without raising. Two cheats
(invincibility and level skip) make a full review of every feature easy.

## General Software Architecture

```
pac-man.py                 -> CLI entry point, validates the .json argument
src/
  __main__.py              -> module entry point
  game_engine/
    config.py              -> config loading, comment stripping, validation
    core.py                -> window, main loop, scene registry
    definitions.py         -> Scene contract and QUIT sentinel
    entities/
      pacman.py            -> player movement and animation
      ghost.py             -> ghost state machine and targeting
    scenes/
      main_menu.py         -> landing screen and mode toggle
      playing_level.py     -> in-game orchestration and HUD
      pause_menu.py        -> pause screen
      scores_menu.py       -> top-ten board
      instructions_menu.py -> how to play and credits
      end_screen.py        -> game over and victory, name entry
    tools/
      level_generation.py  -> adapter over the A-Maze-ing package
      level_tools.py       -> grid loading, moves, item placement
      ghost_ai.py          -> pathfinding and movement policies
      highscore.py         -> persistent top-ten board
    ui/
      components.py        -> Button and TextInput widgets
      theme.py             -> per-mode background colour
data/
  config.json              -> default configuration
  highscores*.json         -> saved boards
tools/
  visualisation_tools      -> fonts, sprites and sounds
```

`pac-man.py` validates the single `.json` argument, then hands the path to
`core.launch`, which sets the configuration path and starts the loop. The rest
of the game reads settings only through `config.py`.

## Project Management

Planning and tracking documents live under `project-management/devnotes`:

- `1-Rules.md` tracks every format, mandatory item, bonus, open point and
  ambiguity from the subject, with a done or not-done state.
- `2-Logic.md` is the system design, one block per module with its boundary,
  inputs, outputs, process, guarantees and errors.
- `3-DebugLog.md` keeps the development log and debug debrief.

These documents record the team decisions, the assumptions made on unclear
points, and the state of the work over time.
