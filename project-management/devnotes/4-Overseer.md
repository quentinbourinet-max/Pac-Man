# 4-Overseer.md - Pacman

| DRAFT Overseer snapshot | Authors: qbourine, jferone | Subject: Pacman v1.4 | Date: 2026-07-08 |
|---|---|---|---|

Supervision view of the whole system across the DRAFT layers, with an integral
audit. Certainty markers: **certain** (verified here by execution, lint or
direct reading) and **sensed** (inferred, not verifiable without a real runner
or an external action).

## Layers

| Layer | Scope | Artefact |
|---|---|---|
| **D0** Order | Capture of the customer order (42 subject) | `0-Order.pdf` |
| **D1** Conditions | FMBOA requirement checklist | `1-Rules.md` |
| **D2** Logic | BIOPGE contract, one block per module | `2-Logic.md` |
| **D3** Embodiment | Source code + dev journal | `src/`, `3-DebugLog.md` |
| **D4** Delivery | Packaging, deployment, review-readiness | `pyproject`/`deps`/CI/README/Itch.io |

## Master table

| Layer | Completion | Conformity | Certainty | Evidence |
|---|---|---|---|---|
| **D0** | 100% | 100% | certain | PDF present; requirements extracted into D1; version v1.4 confirmed. |
| **D1** | 100% | 100% | certain | 60/60 mandatory (M55 deployed); F/B/O/A all closed; M3/A5/M21 fully resolved and re-synced. |
| **D2** | 97% | 97% | certain | All BIOPGE blocks mirror the refactored code (models+parser, mazegen, uv, clamp); cross-block I/O consistent; IDs traced. |
| **D3** | 99% | 99% | certain (code+visual) | `make lint` + `lint-strict` green; 0 docstring gaps; every scene visually verified; config crash-proof; 4.1-4.6 fixed. |
| **D4** | 93% | 93% | certain / sensed | Itch.io live; wheel+uv+CI+README+PM docs done. Package regen at review (M57) and CI on a real runner remain sensed. |

## D1 - FMBOA breakdown (all closed)

| Category | State | Note |
|---|---|---|
| F (Formats) | 22/22 | lint (both), docstrings, type hints, Makefile, README structure. |
| M (Mandatory) | 60/60 | includes M55 (Itch.io deploy). M3/M5/A5 fully robust (per-key clamp). |
| B (Bonus) | 4/4 | B1 `lint-strict` genuinely green; B2 comments; B3 cheats; B4 modes. |
| O (Open points) | 7/7 | decisions locked. |
| A (Ambiguities) | 8/8 | A2 (mazegen), A5 (robust config), A6 (item placement) resolved. |

## D3 - verification evidence (certain)

- **Lint**: `make lint` and `make lint-strict` both report "Success: no issues".
- **Docstrings**: AST coverage check = 0 gaps (module, class, method).
- **Translation**: 0 French artefact, 0 em dash across code and docs.
- **Robustness (M3/A5)**: verified that a broken JSON, zero speeds and
  out-of-range window all keep the game running (clamp + playable defaults).
- **Visual (M54)**: menu, level, instructions, scores, victory and game over
  rendered offscreen and inspected; fonts, ghost sprites, HUD, maze, item
  placement (super-pacgums adjacent to corners) and the name field all correct.

## D4 - delivery breakdown

| Item | State | Certainty |
|---|---|---|
| Packaging (`uv sync`, wheel, `pyproject`) | done | certain |
| CI Windows build (PyInstaller) | workflow present, translated | sensed (not run on a runner here) |
| README + in-package instructions (M56) | done, re-synced | certain |
| PM evidence D0-D4 (M58) | done | certain |
| Public platform deploy (M55) | done (Itch.io, unlisted, functional) | reported by author |
| Package regen at peer review (M57) | planned | sensed |

## Global score (weighted: D0 5% - D1 15% - D2 15% - D3 45% - D4 20%)

```
COMPLETION  : ~98%
CONFORMITY  : ~98%   (subject v1.4, as captured in D1)
```

## Residual (non-blocking, sensed)

None of these gates a mandatory requirement.

1. CI actually building on a GitHub runner (M57 regen confidence).
2. Freshness of the Itch.io build versus the current tree.
3. Overseer snapshot is a point-in-time view (2026-07-08); re-run the checks
   after any further change.

Overseer status: **green**. No mandatory item outstanding; the remaining points
are confidence hardening, not conformity gaps.
