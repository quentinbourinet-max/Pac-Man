# TO-DO — Final fixes before eval #2

> **Why we were invalidated:** flake8 **F401** `'src.__main__' imported but unused` in
> `pac-man.py`, caused by a dead block `if False: import src.__main__` + a dynamic launch
> `runpy.run_module("src")`.
> **Fix already applied:** removed the dead block + all the `frozen`/`_MEIPASS`/`base_dir`/
> `sys.path`/`main_script`/`runpy` logic; now a real `import src.__main__` + `src.__main__.main()`
> inside the `try`.
>
> Last updated 2026-07-10. Legend: `[x]` done · `[ ]` to do.

---

## 1. DONE & VERIFIED — nothing left to do here

- [x] **flake8 fix works.** `uv run flake8 src/ pac-man.py` → exit 0. F401 gone, not moved elsewhere.
- [x] **Entry point behaves.** All 3 argv checks (no arg / non-`.json` / missing file) exit 1
      with a clean message, no traceback. Headless run of the game works.
- [x] **PyInstaller packaging still works WITHOUT the dead code — built & ran a real `--onefile`
      binary.** Proven empirically:
  - `src.__main__` **and the whole `src.pacman_engine.*` engine + `mazegen`** are auto-bundled
    (PyInstaller's AST scan follows the real `import`). **No `--hidden-import` needed.**
  - The produced Linux binary launches and runs the game.
  - The `Font not found` message seen mid-test was **not** a regression: assets are opened
    **relative to the current dir**, so the binary must be run with `data/` next to it — which
    is exactly what the CI workflow ships (`release/` = exe + `data/`). Run that way → assets
    load fine. This behavior is unchanged by our fix.

**Bottom line:** the `pac-man.py` fix is **safe to commit as-is.** No workflow change.

---

## 2. TO DO — commit

- [ ] Commit the fix **scoped to `pac-man.py` only**.
      The working tree also has unrelated changes (README, `data/highscores.json`,
      devnotes moved to `DRAFT/`, `src/__init__.py` emptied) → put those in **separate** commits.

## 3. TO DO — docs are now out of sync with the code (D1/D2/D3)

The code no longer uses `runpy` / `sys.path`, but the deliverables still describe the old way:

- [ ] `README.md` (~lines 224-225): says "runs the `src` module (`runpy.run_module`)" → rewrite.
- [ ] `2-Logic.md` (~lines 43-44): entry-point table still mentions `runpy.run_module("src")`
      and "Insert the base dir on `sys.path`" → update to the direct `import src.__main__` call.
- [ ] Quick grep the other devnotes (`1-Rules.md`, `3-Journal.md`, `DRAFT.md`) for leftover
      `runpy` / `base dir` / `sys.path` mentions.

## 4. TO DO — `make lint` still FAILS on mypy (pre-existing, NOT our fix)

`make lint` = `flake8 .` **+ `mypy .`**. mypy reports **5 × `Unused "type: ignore"`** — confirmed
present on HEAD too, so not caused by our change, but the grader runs this same command:

- [ ] Decide (pick one) and apply:
  - **(a)** remove the 5 now-useless `# type: ignore` comments, **or**
  - **(b)** pin the pygame version to the original env.
- [ ] Locations: `entities/pacman.py:42`, `entities/ghost.py:58` & `:63`, `core.py:72` & `:96`.
- [ ] Cause: `pygame-ce` now ships type hints → those ignores became unnecessary.
- [ ] Re-run **`make lint`** → must exit 0 before we call it eval-ready.

## 5. TO DO — gameplay (unrelated to the lint fix)

- [ ] No negative score inputs: reject/rewrite/delete bad values on load; never show a negative
      value in the in-game scoreboard.

---

## Verify-it-yourself commands

```sh
cd Pac-Man
uv run flake8 src/ pac-man.py            # expect exit 0 (fix)
make lint                                # expect exit 0 ONLY AFTER section 4
git diff --stat pac-man.py               # the fix commit must touch this file only
```
