# 3-Journal.md - Pacman

| DRAFT D.3 | Authors: qbourine, jferone | Journal of the implementation phase | Updated: 2026-07-08 |
|---|---|---|---|

The development journal and debug debrief. It records the decisions taken while
turning the `2-Logic.md` contract into code, the big refactor, and the issues
still open at review time.

---

## 1. Development timeline

| Phase | Work | Reference commits |
|---|---|---|
| Bootstrap | Project core architecture; A-Maze-ing (`mazegen`) package integration | `d464f9e`, `94371d2` |
| Maze | Full maze generation; wall-bitmask grid; centred rendering | `17581a4`, `f060435`, `ac966fa` |
| Player | Pac-Man, pacgums, timer, score, lives | `645e713` |
| Ghosts | Four ghosts, collisions, edible state, window scaling | `b29d23b`, `563e31c` |
| AI + menus | Ghost AI (BFS, personalities), pause menu | `6974b06` |
| Screens | End screen, instructions, pause, scores; menu mode button | `31053a2`, `0c23962` |
| Highscore | Persistent board seeded from config | `2331f37` |
| Refactor | Package rename, pydantic config, assets move, packaging, CI | `b0739b1`..`e319e9a` |
| Polish | Translation, docstrings, lint, doc reconciliation | 2026-07-08 (this pass) |

---

## 2. Refactor debrief (qbourine)

A large structural pass reshaped the codebase. Key changes and their rationale:

- **Package rename** `pacman-engine` -> `pacman_engine`, so the directory is a
  valid Python identifier and relative imports work cleanly.
- **Config moved to pydantic**: the hand-rolled `config.py` was replaced by
  typed models in `models/models.py` (schemas, ranges, validators) loaded by
  `tools/parser.py` (comment stripping, accessors, score store). `config.json`
  now also carries `ui.colors`, `scores`, `paths`, `instructions` and `app`.
- **Assets relocated** from `tools/visualisation_tools` to `data/assets`
  (fonts, sprites, music, sfx), with all paths declared in `config.json`.
- **Packaging**: the maze wheel lives in `deps/mazegen-1.0.0-py3-none-any.whl`
  (package `mazegen`, class `MazeGenerator`); dependencies are managed with
  `uv` (`uv sync`); a GitHub Actions workflow builds a Windows executable with
  PyInstaller.
- **Highscores unified** into a single `data/highscores.json`, keyed by mode,
  instead of one file per mode.

---

## 3. Polish and audit pass (2026-07-08)

A final review pass over the refactored code and deliverables:

- **French to English**: every remaining French docstring, comment, log message
  and CI step name was translated (`models.py`, `parser.py`, `ghost.py`,
  `theme.py`, `pyproject.toml`, `.github/workflows/build-windows.yml`). Warning
  prints were unified to a single English style.
- **Docstrings (F6)**: every module, class, function and method carries a
  docstring; empty package `__init__.py` files are intentionally left bare.
  AST coverage reports **0 gaps** across all non-empty modules, classes and methods.
- **Lint**: `make lint` was failing with five `Unused "type: ignore"` errors;
  the stale ignores were removed. `flake8` and `mypy` (Makefile flags) are green.
- **Imports**: two `TYPE_CHECKING` imports used a non-relative `from tools.parser`
  path; fixed to relative. Added the missing `models/__init__.py`.
- **Documentation reconciliation**: the root `README.md`, `2-Logic.md` and
  `1-Rules.md` were brought back in line with the refactored code (package name,
  config blocks, wheel path, `uv`, highscore layout, maze adapter signature).

---

## 4. Issues found and resolved (2026-07-08)

Found during the audit pass and treated in order of weight. Kept here as a
traceable record for the reviewer.

### 4.1 Invalid shipped config crashed `make run` (FIXED)
`data/config.json` had `levels.dims[0] = [1, 10]`, which violated the
`validate_level_dimensions` rule (minimum 10x10) added in commit `e319e9a`.
Validation failed, the whole config was discarded, and the defaults left
`paths=None`, tripping `assert self.config.paths is not None` in `core.Game`:
the game exited with code 1 on the default config. **Fixed** by correcting the
entry to `[10, 10]`, and hardened structurally by 4.2 below.

### 4.2 Config robustness (M3 / A5) (FIXED)
The subject wants an invalid value clamped to a safe default so the game keeps
running, and states the config may be edited at defense. Two changes make this
hold:
- `PathsConfig` fields now default to the standard `data/` layout, and
  `GameConfigRoot.paths` defaults to a `PathsConfig()`. A defaults-only config
  (missing/invalid file) is therefore always playable and never leaves
  `paths=None`.
- `LevelsConfig.validate_level_dimensions` now **clamps** each `dims` entry into
  `10..50` and drops malformed pairs instead of raising, so an edited `dims`
  no longer discards the config.

Verified: a `[1, 999]` edit clamps to `(10, 50)` with the other custom values
preserved; a syntactically broken JSON boots on playable defaults. The former
per-field residual was then closed in the hardening pass (section 5): every
numeric field now clamps, so no single field can discard the config.

### 4.3 Super-pacgum placement (A6 / M21) (FIXED)
A mid-audit commit had moved the super-pacgums off the corners onto the adjacent
cells, following a drifted reading of A6/M21. D0 (VI.1/VI.4) states super-pacgums
sit **in the 4 corners of the maze**, so it was reverted: `init_item_grid` places
each super-pacgum (item `2`) directly **on** the four corner cells (shared with
the ghost spawns), every other open corridor cell gets a pacgum, and the Pac-Man
start cell is excluded. D1 (M21/A6) and D2 (`level_tools`) were re-synced to match.
Verified at runtime: supers land on (0,0), (0,W-1), (H-1,0), (H-1,W-1).

### 4.4 Pac-Man start cell not excluded from pacgums (FIXED)
`init_item_grid(exclude=...)` receives a single `[col, row]` but tested
`[c, r] in exclude`, comparing a coordinate against a list of ints (always
false; flagged by `mypy --strict` as a non-overlapping container check). Changed
to `[c, r] == exclude`, so Pac-Man's start cell is now genuinely gum-free.

### 4.5 `make lint-strict` (mypy --strict) not clean (FIXED)
The real typing nits were fixed: three `dict` annotations parametrised in
`parser.py` (`get_gamemode_cfg`, `get_scores`, `save_score`) and a now-redundant
`cast` removed from `highscore.py`. The remaining `--strict` errors were all
missing third-party stubs (`pygame`, `mazegen` ship none), so the `lint-strict`
rule now runs `mypy --strict --ignore-missing-imports`. Both `make lint` and
`make lint-strict` are green; the bonus B1 is genuinely satisfied.

### 4.6 Deep relative imports (FIXED)
Several modules used `from ...pacman_engine.tools...` (three dots), which
resolved only because `pac-man.py` runs `src` as the top-level package. Rewritten
to conventional package-relative imports (`..tools`, `..entities`, `.module`) in
the hardening pass (section 5); behaviour identical, fragility removed.

---

## 5. Hardening pass (2026-07-08, second)

Optional robustness and cleanliness work beyond the mandatory scope, plus a
full visual verification.

- **Full per-key config clamp (C1)**: `WindowConfig` and `LevelsConfig` gained
  `model_validator(mode='before')` clamps (out-of-range values are clamped, not
  rejected). `get_gamemode_cfg` now starts from the `CommonGameConfig` /
  `ModeConfig` defaults (previously dead schema), backfills every consumed key,
  clamps each game numeric to its safe range and repairs invalid duration lists.
  This closes the crash vectors an edited config could still hit: missing keys
  (`KeyError`) and zero speeds (`ZeroDivisionError`). Verified end-to-end.
- **Deep imports (C2, 4.6)**: rewritten to conventional relative imports.
- **Dead asserts (A2)**: removed the now-vacuous `assert ... paths is not None`
  (paths always resolves since 4.2). A now-redundant `cast` in `level_tools`
  and `highscore` was dropped as a consequence.
- **Makefile (C3)**: `flake8` now also lints `pac-man.py`.
- **Visual verification (B1)**: every scene rendered offscreen and inspected
  (menu, level, instructions, scores, victory, game over). Fonts, ghost sprites,
  HUD, maze, item placement and the name-entry field all render correctly,
  confirming M54 (polished UI) beyond the headless run.

Final state: `make lint` and `make lint-strict` both green, 0 docstring gaps,
no French, no em dashes, no config edit crashes the game.
