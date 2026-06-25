# 2-Logic.md - Pacman

| DRAFT D.2 | Authors: qbourine, jferone | Based on: 1-Rules.md (2026-06-14) | Date: 2026-06-15 |
|---|---|---|---|

---

## GLOBAL VIEW

`pac-man.py` (repo root) validates the single `.json` CLI arg and hands the path to
the engine. `config.py` loads it (comments stripped, values clamped, unknown keys
ignored) into a defaults-backed settings object. `core.Game` owns the window and the
one main loop; it drives exactly one active `Scene` per frame
(`handle_events -> update -> render`). Pausing swaps to a `PauseMenu` scene while the
play scene is kept aside and frozen, then restored on resume. Scenes request
transitions by name through a registry. `highscore.py` loads the board at start and saves it at game end.
Maze data comes from the externally-assigned A-Maze-ing package (`mazegenerator`, used
as-is) through a single isolated adapter (`level_generation.MazeAdapter`); `level_tools`
turns a maze grid into a walkable/item model the entities read through `is_move_possible`.

---

## SYSTEM VIEW

> **System view:** BIOPGE logic blocks v1.0 (Sayca Labs)

<details>
<summary>`pac-man.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: the repo-root CLI entry point, argument validation, the `sys.path` bootstrap and the process exit code. NOT: config parsing, game logic, rendering. |
| **Inputs** | `argv`: exactly one path that ends in `.json` and exists on disk. |
| **Outputs** | Process exit code via `sys.exit`; delegates the run to `core.launch(config_path)`. |
| **Process** | 1. Check `argc == 2` else print usage -> 2. Check the argument ends with `.json` -> 3. Check the file exists -> 4. Insert `src/` on `sys.path` -> 5. Call `core.launch(config_path)` and return its code. |
| **Guarantees** | Exactly one existing `.json` path reaches the engine; any misuse yields a clear message and a non-zero exit, never a Python traceback. |
| **Errors** | wrong argc / non-`.json` / missing file -> printed message, exit 1. |

> Covers : F16, F17, F18, M1

</details>

<details>
<summary>`src/ __main__.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: the `python -m` module entrypoint + process exit code. NOT: argument parsing (uses the bundled default config), game logic. |
| **Inputs** | none (no CLI argument; the default `data/config.json` is used). |
| **Outputs** | process exit code returned by `core.launch()`. |
| **Process** | 1. Call `core.launch()` with no path (default config) -> 2. `sys.exit` its return code. |
| **Guarantees** | A no-argument launch convenience for `python -m`; the graded CLI stays `pac-man.py`; errors are handled inside `core.launch`. |
| **Errors** | delegated to `core.launch`: `KeyboardInterrupt` -> exit 130, any other exception -> clear message + exit 1. |

> Covers : M1
</details>

<details>
<summary>`src/ game_engine/ config.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: reading the config file, defaults, clamping, key filtering, and merging shared defaults with the active game-mode preset. NOT: CLI, file path choice. |
| **Inputs** | `path`: str to a `.json` file with `#` / `//` line and `/* */` block comments (B2); `mode`: active preset name (default `original`); `level`: index for per-level dims/seed. |
| **Outputs** | A settings object exposing every key with a valid value (window; `levels` width/height + per-level `dims[]` + `seed` (level 1 only); points; entity speeds: ghost/frightened/dead-mult/pacman + collision ratio + per-mode `speed_multiplier` (1.0 original, 1.3 ironman); lives, times, highscore filename, frightened/respawn durations), built as `common` defaults overridden by the selected mode preset. Helpers: `get_window_cfg`, `get_gamemode_cfg`, `get_levels_cfg`, `get_level_dims(level)`, `get_level_seed`, `get_highscore_path(mode)`. |
| **Process** | 1. Read file -> 2. `_strip_comments` removes `#`/`//`/`/* */`, full-line or trailing, string-aware -> 3. Parse JSON -> 4. Merge `common` + selected mode override -> 5. `_validate_value` per consumed key: coerce to type, clamp to schema range, else fall back to default + log -> 6. Ignore unknown keys -> 7. Return settings. |
| **Guarantees** | Every consumed key is present, correctly typed and within range after the call; comment markers inside JSON strings survive; unknown keys never raise; a missing/corrupt file yields full defaults; the engine reads settings only through this object (no direct `config.json` read elsewhere). The `common + override` merge stays mode-agnostic; the B4 mode selector cycles presets without contract change. |
| **Errors** | missing/unreadable/invalid JSON -> log clear message, return defaults. invalid/out-of-range value -> coerce/clamp or fall back to default + log, continue. unknown mode -> fall back to `original` + log. |

> Covers : F19, M2, M3, M4, M5, B2, B4, A1, A3, A5, A8, O1, O4
</details>

<details>
<summary>`src/ game_engine/ core.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: window (incl. F11 fullscreen toggle), clock, main loop, scene registry, pause swap. NOT: per-scene logic, drawing of game entities. |
| **Inputs** | settings object; scene transition names returned by the active scene; the F11 key. |
| **Outputs** | Frames on screen; scene swaps; process returns when `running` is false. |
| **Process** | 1. Init window from settings -> 2. Set active scene = main_menu -> 3. Loop: collect events (F11 toggles fullscreen) -> 4. scene.handle_events -> 5. scene.update -> 6. scene.render -> 7. flip -> 8. apply requested transition. Pause: `pause_game` stores the play scene aside and swaps to `PauseMenu`; `resume_game` restores it. |
| **Guarantees** | Exactly one scene active at a time; the paused play scene is frozen but restored intact on resume; `QUIT` ends the loop and releases pygame. |
| **Errors** | unknown scene name -> ignored/logged, stay on current scene. pygame init failure -> propagate to entry as handled error. |

> Covers : F7, F8, M45, M48, M51, O5
</details>

<details>
<summary>`src/ game_engine/ definitions.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: the `Scene` abstract contract + the `QUIT` sentinel. NOT: any concrete behavior. |
| **Inputs** | none (interface only). |
| **Outputs** | `handle_events -> scene name / QUIT / None`; `update(dt)`; `render(surface)`. |
| **Process** | 1. Declare abstract methods -> 2. Concrete scenes implement them. |
| **Guarantees** | Engine can swap any scene without knowing its type; returning None means "stay". |
| **Errors** | n/a (abstract). |

> Covers : F7
</details>

<details>
<summary>`src/ game_engine/ scenes/ main_menu.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: landing screen + navigation entries + game-mode toggle. NOT: gameplay, highscore storage. |
| **Inputs** | mouse/keyboard events; window size (for proportional layout); configured mode list (`game.*` presets). |
| **Outputs** | transition name: level / scores / instructions / QUIT; side-effect: sets `game.mode` via the MODE toggle. |
| **Process** | 1. Build buttons proportional to window (incl. a MODE button) -> 2. On MODE click: cycle to the next configured preset + refresh label, stay on menu -> 3. On other click/key: return target. |
| **Guarantees** | Items present: Start Game, MODE toggle (Original/Ironman/...), View Highscores, Instructions, Exit. The selected mode drives gameplay constants and the per-mode highscore file. (Credits folded into the instructions screen, see below.) |
| **Errors** | font missing -> fallback system font + log; mode absent from config -> fall back to first available. |

> Covers : M49, M54, M17, B4
</details>

<details>
<summary>`src/ game_engine/ scenes/ instructions_menu.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: static controls/options/config help screen + credits footer. NOT: changing settings. (Single screen: subject requires Instructions, not a separate Settings/Credits; the existing `credits_menu.py` is renamed into this one, `settings_menu.py` is dropped.) |
| **Inputs** | events (ESC/click to return). |
| **Outputs** | transition main_menu. |
| **Process** | 1. Render help text (controls / options / config keys / cheat activation) -> 2. Render credits at the bottom -> 3. Return main_menu on input. |
| **Guarantees** | Controls, options, cheat activation and authors' credits are listed. |
| **Errors** | font missing -> fallback + log. |

> Covers : M49, M56, M40
</details>

<details>
<summary>`src/ game_engine/ scenes/ playing_level.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: per-level orchestration (entities, scoring, lives, timer, win/lose, HUD) + the global scatter/chase clock it feeds to ghosts. NOT: AI internals, maze parsing, persistence. |
| **Inputs** | settings; movement keys (arrows/WASD); pause + cheat keys; frame dt. |
| **Outputs** | score/lives/level/time state; current scatter/chase phase passed to ghosts; transition to end_screen (win/lose) or pause request. |
| **Process** | 1. Load level grid + item grid, place Pac-Man center, ghosts in corners -> 2. Each frame: tick the scatter/chase clock (frozen while frightened) and advance ghosts (with the phase) + Pac-Man -> 3. Resolve collisions (normal ghost: lose life + respawn + reset phase; edible ghost: +Z, ghost to eyes-state) -> 4. Eat pacgum +X / super-pacgum +Y + ghosts frightened -> 5. timer hits 0 -> lose a life + reset level -> 6. all gums gone -> next level (keep score+lives) -> 7. last level cleared -> victory. |
| **Guarantees** | Score never decreases; Pac-Man only enters corridor cells; score+lives carried across levels; HUD always shows score/lives/level/time; scatter/chase alternation follows the configured durations. |
| **Errors** | missing assets (sound/font/sprite) -> silent/fallback + log, gameplay continues. |

> Covers : M20-M34, M39, M40, M42-M45, M50, A6, A7, O3, O4 |

</details>

<details>
<summary>`src/ game_engine/ scenes/ scores_menu.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: rendering the Top 10. NOT: writing the board. |
| **Inputs** | board from `highscore.py` (path = `get_highscore_path(game.mode)`); events to return. |
| **Outputs** | transition main_menu. |
| **Process** | 1. Read the active mode's board -> 2. Render up to 10 (name + score) -> 3. Return on input. |
| **Guarantees** | At most 10 entries shown, sorted by score desc; board matches the selected mode. |
| **Errors** | empty/missing board -> show "no scores yet". |

> Covers : M14, M17
</details>

<details>
<summary>`src/ game_engine/ scenes/ end_screen.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: game-over AND victory screen + name entry. NOT: score computation. |
| **Inputs** | final score; outcome (win/lose); typed name via TextInput; active mode (selects the highscore file via `get_highscore_path(game.mode)`). |
| **Outputs** | save (name, score) to the active mode's board through `highscore.py`; transition main_menu. |
| **Process** | 1. Show outcome + final score (victory adds congrats) -> 2. Prompt name -> 3. Validate name -> 4. Save -> 5. Return main_menu. |
| **Guarantees** | Name <= 10 chars, alphanumeric + spaces; score saved as non-negative int. |
| **Errors** | invalid name -> reject keystroke; save failure -> log, still return to menu. |

> Covers : M16, M46, M47, M52, M53, M12, M13
</details>

<details>
<summary>`src/ game_engine/ scenes/ pause_menu.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: the pause screen (Resume / Main Menu) drawn over a frozen snapshot of the play scene. NOT: gameplay logic; the play scene is kept aside by `core`, not advanced. |
| **Inputs** | events; the snapshot surface captured by `core.pause_game`. |
| **Outputs** | resume (back to the stored play scene) or transition main_menu. |
| **Process** | 1. Dim the snapshot -> 2. Draw the PAUSE title + buttons -> 3. ESC or Resume calls `resume_game`; Main Menu swaps to main_menu. |
| **Guarantees** | The play scene underneath is frozen but restored intact on resume; music pauses and resumes with it. |
| **Errors** | font missing -> fallback system font. |

> Covers : M45, M51
</details>

<details>
<summary>`src/ game_engine/ ui/ components.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: reusable widgets (Button, TextInput). NOT: scene logic. |
| **Inputs** | events; geometry; font. |
| **Outputs** | Button -> click bool; TextInput -> validated string. |
| **Process** | Button: 1. track hover -> 2. report left-click inside. TextInput: 1. accept allowed chars up to max -> 2. expose current value. |
| **Guarantees** | TextInput never exceeds its max length nor accepts disallowed chars. |
| **Errors** | n/a (pure input handling). |

> Covers : M12, M54
</details>

<details>
<summary>`src/ game_engine/ ui/ theme.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: the per-mode scene background colour. NOT: drawing, scene logic, any other styling. |
| **Inputs** | the active mode name; the scene's own default background colour. |
| **Outputs** | a single RGB tuple: the Ironman purple when the mode is `ironman`, otherwise the scene's default. |
| **Process** | 1. `background(mode, default)` returns `IRONMAN_BG` if `mode == "ironman"` else `default`. |
| **Guarantees** | Original mode keeps every scene's own colour unchanged; Ironman gives all scenes one pronounced purple from a single source of truth (`pause_menu` inherits it through the frozen snapshot). |
| **Errors** | n/a (pure function). |

> Covers : B4, M54
</details>

<details>
<summary>`src/ game_engine/ entities/ pacman.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: player position, buffered direction, grid movement, animation. NOT: collisions with ghosts, scoring. |
| **Inputs** | requested direction; frame dt; `LevelTools` for wall checks. |
| **Outputs** | grid coord, pixel position (interpolated), "changed tile" flag. |
| **Process** | 1. Buffer next_dir -> 2. on move tick: take next_dir if legal else keep dir -> 3. step one cell if legal else stop. |
| **Guarantees** | Never enters a wall/closed cell; respawns at maze center on demand. |
| **Errors** | sprites missing -> draw yellow circle fallback + log. |

> Covers : M23, M24, M25, M28
</details>

<details>
<summary>`src/ game_engine/ entities/ ghost.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: one ghost's state machine + per-personality targeting AI. NOT: detecting contact with Pac-Man. |
| **Inputs** | frame dt; base speed; dead-speed multiplier; `LevelTools`; Pac-Man coord+direction; global scatter/chase `phase`. |
| **Outputs** | grid coord, direction, state (normal / scared / dead-eyes). |
| **Process** | 1. In `chase` phase, pick target per personality: Blinky=Pac-Man tile; Pinky=4 ahead; Clyde=Pac-Man if far (>8) else bottom-left corner -> in `scatter` phase a normal ghost heads to its home corner (its spawn), milling around it once reached. **Inky always wanders randomly (deliberate design choice).** -> 2. frightened (scared) -> flee away from Pac-Man + slow + recolor -> 3. eaten -> eyes return to spawn (BFS, double speed), then rejoin normal on arrival -> 4. BFS shortest path toward target, avoiding an immediate U-turn. |
| **Guarantees** | Moves only through corridors; scatter sends it home, chase sends it after its target; flees while edible; eaten ghost rejoins once its eyes reach the spawn. |
| **Errors** | no legal non-reverse move -> allow reverse rather than freeze. |

> Covers : M22, M35, M36, M37, M38, A3, A4, O3
</details>

<details>
<summary>`src/ game_engine/ tools/ level_generation.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: a single isolated adapter (`MazeAdapter`) over the externally-assigned A-Maze-ing package (`mazegenerator`, used as-is) + the `generate_grid(level)` helper. NOT: rendering, item placement, persistence, modifying the package. The rest of the game never imports the generator directly. |
| **Inputs** | level index; dims + level seed from settings (`get_level_dims`, `get_level_seed`). |
| **Outputs** | a fresh maze grid (wall-bitmask per cell), in memory; `[]` on failure. |
| **Process** | 1. `generate_grid(level)` reads dims + seed -> 2. `MazeAdapter.generate(seed)` calls `MazeGenerator(size, perfect=False, entry_cell, exit_cell, seed)` and reads `.maze`. Level 1 uses the fixed `levels.seed` (reproducible, package is deterministic for `seed > 0`); later levels get `seed=None` -> random maze each call (subject VI.1). No file persistence. **A future package version touches only `MazeAdapter._build` (see ADAPTER CONTRACT).** |
| **Guarantees** | Loader adapts to the package interface (not the opposite); package used unmodified; corridors are Pac-Man-compatible (`perfect=False`); level 1 reproducible, subsequent levels randomly generated; at least 10 levels available. |
| **Errors** | generator failure -> log + return `[]` (caller handles), no crash. |

> Covers : M6, M7, M8, M9, M10, M18, M19, M41, A2, A8
</details>

<details>
<summary>`src/ game_engine/ tools/ level_tools.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: requesting a level's grid (via `generate_grid`), building the item grid, wall-aware move checks, win check. NOT: generation internals, entity state. |
| **Inputs** | level index; item grid; coord + direction. |
| **Outputs** | maze grid; item grid (0 empty / 1 pacgum / 2 super); move-legal bool; level-complete bool. |
| **Process** | 1. `load_map` asks `generate_grid(level)` for an in-memory grid -> 2. `find_central_open_cell()` = open cell nearest the real centre (Pac-Man spawn) -> 3. seed an RNG with the level seed (level 1 fixed, later levels `None` -> random); place a super-pacgum on an open cell adjacent to each corner; fill the other accessible corridor cells with pacgums, excluding the 4 corner ghost spawns and Pac-Man's start -> 4. move check tests both cells' shared edge bits -> 5. complete when no item > 0 remains. |
| **Guarantees** | A move blocked by a wall bit is always rejected; Pac-Man never spawns in a wall; super-pacgums sit next to (not on) the corner spawns; level 1 placement is reproducible, later levels vary. |
| **Errors** | empty grid (generator failure) -> log + return empty (caller handles). |

> Covers : M20, M21, M23, M28, M30, M24, A6, A7
</details>

<details>
<summary>`src/ game_engine/ tools/ highscore.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: persistent Top-10 board on disk. NOT: name entry UI, scoring. |
| **Inputs** | highscore filename (from settings); (name, score) to insert. |
| **Outputs** | sorted Top-10 list; updated file on save. |
| **Process** | 1. Load at start (tolerate missing/invalid) -> 2. Insert -> sort desc -> trim to 10 -> 3. Save at game end via context manager. |
| **Guarantees** | <= 10 entries; names <= 10 chars alphanumeric+spaces; scores non-negative ints; file errors never crash. |
| **Errors** | missing/corrupt file -> start from empty board + log. write failure -> log, keep running. |

> Covers : F3, F4, M11, M12, M13, M14, M15, O2
</details>

---

### D.2 exit checklist
- [x] Gate applied: full BIOPGE (>3 interfaces)
- [x] All blocks complete
- [x] `> Covers :` traces every D.1 ID at least once
- [x] Cross-block I/O consistent (config -> engine -> scenes -> tools/highscore)
