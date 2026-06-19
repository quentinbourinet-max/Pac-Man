# 2-Logic.md - Pacman

| DRAFT D.2 | Authors: qbourine, jferone | Based on: 1-Rules.md (2026-06-14) | Date: 2026-06-15 |
|---|---|---|---|

---

## GLOBAL VIEW

`pac-man.py` (repo root) validates the single `.json` CLI arg and hands the path to
the engine. `config.py` loads it (comments stripped, values clamped, unknown keys
ignored) into a defaults-backed settings object. `core.Game` owns the window and the
one main loop; it drives exactly one active `Scene` per frame
(`handle_events -> update -> render`) and may stack one `Overlay` (pause) that freezes
`update` while the scene stays drawn underneath. Scenes request transitions by name
through a registry. `highscore.py` loads the board at start and saves it at game end.
Maze data comes from the assigned A-Maze-ing package via a thin loader; `level_tools`
turns a maze grid into a walkable/item model the entities read through `is_move_possible`.

---

## SYSTEM VIEW

> **System view:** BIOPGE logic blocks v1.0 (Sayca Labs)

<details>
<summary>`__main.py__`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: CLI contract + process exit code. NOT: config parsing, game logic. |
| **Inputs** | `argv`: exactly one path ending in `.json`. |
| **Outputs** | Exit code (0 ok, non-zero on handled error); delegates to `core.run(path)`. |
| **Process** | 1. Check argc == 2 -> 2. Check arg ends `.json` -> 3. Call `run(path)` -> 4. Map exceptions to a clear message + code. |
| **Guarantees** | No Python traceback ever reaches stdout/stderr; one and only one config path passed downstream. |
| **Errors** | wrong argc / non-`.json` -> printed usage, exit non-zero. `KeyboardInterrupt` -> clean message, exit 130. |

> Covers : F16, F17, F18, M1
</details>

<details>
<summary>`game_engine/ config.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: reading the config file, defaults, clamping, key filtering, and merging shared defaults with the active game-mode preset. NOT: CLI, file path choice. |
| **Inputs** | `path`: str to a `.json`-with-`#`-comments file; `mode`: active preset name (default `original`). |
| **Outputs** | A settings object exposing every key with a valid value (window, lives, times, points, seed, level dims, highscore filename, frightened/respawn durations), built as `common` defaults overridden by the selected mode preset. |
| **Process** | 1. Read file -> 2. Drop lines starting `#` -> 3. Parse JSON -> 4. Merge `common` + selected mode override -> 5. For each known key: take value if valid else clamp to default + log -> 6. Ignore unknown keys -> 7. Return settings. |
| **Guarantees** | Every documented key is present and within range after the call; unknown keys never raise; a missing/corrupt file yields full defaults; the engine reads settings only through this object (no direct `config.json` read elsewhere). Single mode shipped, but the `common + override` merge stays mode-agnostic so the B4 selector grafts in without contract change. |
| **Errors** | missing/unreadable/invalid JSON -> log clear message, return defaults. invalid value -> clamp + log, continue. unknown mode -> fall back to `common` only + log. |

> Covers : F19, M2, M3, M4, M5, B4, A1, A3, A5, A8, O1, O4
</details>

<details>
<summary>`game_engine/ core.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: window, clock, main loop, scene registry, overlay stack. NOT: per-scene logic, drawing of game entities. |
| **Inputs** | settings object; scene transition names returned by the active scene. |
| **Outputs** | Frames on screen; scene swaps; process returns when `running` is false. |
| **Process** | 1. Init window from settings -> 2. Set active scene = main_menu -> 3. Loop: collect events -> 4. if overlay active: overlay.handle_events else scene.handle_events -> 5. scene.update only if no overlay (freeze) -> 6. scene.render, then overlay.render if any -> 7. flip -> 8. apply requested transition / open-close overlay. |
| **Guarantees** | Exactly one scene active at a time; while an overlay is up the scene state does not advance but stays visible; `QUIT` ends the loop and releases pygame. |
| **Errors** | unknown scene name -> ignored/logged, stay on current scene. pygame init failure -> propagate to entry as handled error. |

> Covers : F7, F8, M45, M48, M51, O5
</details>

<details>
<summary>`game_engine/ definitions.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: the `Scene` and `Overlay` abstract contracts + the `QUIT` sentinel. NOT: any concrete behavior. |
| **Inputs** | none (interface only). |
| **Outputs** | `handle_events -> scene name / QUIT / None`; `update(dt)`; `render(surface)`. Overlay adds a "close" signal. |
| **Process** | 1. Declare abstract methods -> 2. Concrete scenes/overlays implement them. |
| **Guarantees** | Engine can swap any scene without knowing its type; returning None means "stay". |
| **Errors** | n/a (abstract). |

> Covers : F7
</details>

<details>
<summary>`game_engine/ scenes/ main_menu.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: landing screen + navigation entries. NOT: gameplay, highscore storage. |
| **Inputs** | mouse/keyboard events; window size (for proportional layout). |
| **Outputs** | transition name: level / scores / instructions / QUIT. |
| **Process** | 1. Build buttons proportional to window -> 2. On click/key return target. |
| **Guarantees** | Items present: Start Game, View Highscores, Instructions, Exit. (Credits folded into the instructions screen, see below.) |
| **Errors** | font missing -> fallback system font + log. |

> Covers : M49, M54, M17
</details>

<details>
<summary>`game_engine/ scenes/ instructions_menu.py`</summary>

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
<summary>`game_engine/ scenes/ playing_level.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: per-level orchestration (entities, scoring, lives, timer, win/lose, HUD). NOT: AI internals, maze parsing, persistence. |
| **Inputs** | settings; movement keys (arrows/WASD); pause + cheat keys; frame dt. |
| **Outputs** | score/lives/level/time state; transition to end_screen (win/lose) or pause overlay request. |
| **Process** | 1. Load level grid + item grid, place Pac-Man center, ghosts in corners -> 2. Each frame: update ghosts + Pac-Man -> 3. Resolve collisions (normal ghost: lose life + respawn; edible ghost: +Z, ghost to eyes-state) -> 4. Eat pacgum +X / super-pacgum +Y + ghosts frightened -> 5. timer hits 0 -> lose a life + reset level -> 6. all gums gone -> next level (keep score+lives) -> 7. last level cleared -> victory. |
| **Guarantees** | Score never decreases; Pac-Man only enters corridor cells; score+lives carried across levels; HUD always shows score/lives/level/time. |
| **Errors** | missing assets (sound/font/sprite) -> silent/fallback + log, gameplay continues. |

> Covers : M20-M34, M39, M40, M42-M45, M50, A6, A7, O4 |

</details>

<details>
<summary>`game_engine/ scenes/ scores_menu.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: rendering the Top 10. NOT: writing the board. |
| **Inputs** | board from `highscore.py`; events to return. |
| **Outputs** | transition main_menu. |
| **Process** | 1. Read board -> 2. Render up to 10 (name + score) -> 3. Return on input. |
| **Guarantees** | At most 10 entries shown, sorted by score desc. |
| **Errors** | empty/missing board -> show "no scores yet". |

> Covers : M14, M17
</details>

<details>
<summary>`game_engine/ scenes/ end_screen.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: game-over AND victory screen + name entry. NOT: score computation. |
| **Inputs** | final score; outcome (win/lose); typed name via TextInput. |
| **Outputs** | save (name, score) through `highscore.py`; transition main_menu. |
| **Process** | 1. Show outcome + final score (victory adds congrats) -> 2. Prompt name -> 3. Validate name -> 4. Save -> 5. Return main_menu. |
| **Guarantees** | Name <= 10 chars, alphanumeric + spaces; score saved as non-negative int. |
| **Errors** | invalid name -> reject keystroke; save failure -> log, still return to menu. |

> Covers : M16, M46, M47, M52, M53, M12, M13
</details>

<details>
<summary>`game_engine/ ui/ components.py`</summary>

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
<summary>`game_engine/ ui/ pause_hud.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: the pause Overlay (Resume / Return to main menu) drawn over any scene. NOT: being a registry scene; the scene stays alive underneath. |
| **Inputs** | events; the surface already holding the frozen scene. |
| **Outputs** | close signal (resume) or transition main_menu. |
| **Process** | 1. On open: pause music -> 2. Draw dim overlay + options -> 3. Resume -> close + resume music; Return -> transition main_menu. |
| **Guarantees** | While open the scene's `update` is not called (state frozen) but remains visible; reusable on any future scene. |
| **Errors** | n/a. |

> Covers : M45, M51
</details>

<details>
<summary>`game_engine/ entities/ pacman.py`</summary>

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
<summary>`game_engine/ entities/ ghost.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: one ghost's state machine + authentic targeting AI. NOT: detecting contact with Pac-Man. |
| **Inputs** | frame dt; speed; `LevelTools`; Pac-Man coord+direction; Blinky coord (for Inky); global scatter/chase phase. |
| **Outputs** | grid coord, direction, state (chase / scatter / frightened / eyes). |
| **Process** | 1. Pick target tile per personality: Blinky=Pac-Man tile; Pinky=4 ahead; Inky=Blinky->2-ahead vector doubled; Clyde=Pac-Man if far else own corner -> 2. scatter phase -> own corner -> 3. frightened -> flee/random + slow + recolor -> 4. eaten -> eyes return to spawn, then after delay rejoin normal -> 5. at each junction step toward target without reversing. |
| **Guarantees** | Moves only through corridors when not in eyes-state; flees while edible; eaten ghost rejoins after the configured 5-10s delay. |
| **Errors** | no legal non-reverse move -> allow reverse rather than freeze. |

> Covers : M22, M35, M36, M37, M38, A3, A4, O3
</details>

<details>
<summary>`game_engine/ tools/ level_generation.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: thin adapter over the assigned A-Maze-ing package; persisting generated levels. NOT: rendering, item placement, modifying the package. |
| **Inputs** | level index; dims/seed from settings. |
| **Outputs** | maze grid (wall-bitmask per cell) written to `data/levels/level_N`. |
| **Process** | 1. Call package with `perfect=False` -> 2. level 1 uses fixed seed (42), others random -> 3. Adapt return to our grid -> 4. Save. |
| **Guarantees** | Loader adapts to the package as-is; corridors are Pac-Man-compatible; at least 10 levels available. |
| **Errors** | generator failure -> handled cleanly (log + abort that level, no crash). |

> Covers : M6, M7, M8, M9, M10, M18, M19, M41, A2, A8
</details>

<details>
<summary>`game_engine/ tools/ level_tools.py`</summary>

| Field | Content |
|---|---|
| **Boundary** | Owns: loading a saved level, building the item grid, wall-aware move checks, win check. NOT: generation, entity state. |
| **Inputs** | level index; item grid; coord + direction. |
| **Outputs** | maze grid; item grid (0 empty / 1 pacgum / 2 super); move-legal bool; level-complete bool. |
| **Process** | 1. Read `level_N` into int grid -> 2. Fill corridors with pacgums, 4 corners with super-pacgums, exclude center + ghost spawns -> 3. move check tests both cells' shared edge bits -> 4. complete when no item > 0 remains. |
| **Guarantees** | A move blocked by a wall bit is always rejected; super-pacgums only at the 4 corners. |
| **Errors** | missing level file -> log clear message, return empty grid (caller handles). |

> Covers : M20, M21, M30, M24, A6, A7
</details>

<details>
<summary>`game_engine/ tools/ highscore.py`</summary>

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
