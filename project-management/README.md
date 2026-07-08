# Project Management

*Planning, tracking and debugging evidence for the 42 Pac-Man project by qbourine and jferone.*

This directory holds the process evidence required by the subject (section VIII).
The work was driven with **DRAFT**, jferone's system-development protocol (see `devnotes/DRAFT.md`):
conditions, then logic, then implementation.

## Structure

```
project-management/
  README.md                -> this index
  devnotes/
    0-Order.pdf            -> the customer order: the 42 subject (PDF)
    1-Rules.md             -> D.1 Conditions: the FMBOA requirement checklist
    2-Logic.md             -> D.2 Logic: the BIOPGE contract, one block per unit
    3-DebugLog.md          -> D.3 Embodiment: dev journal + debug debrief
    4-Overseer.md          -> D.4 supervision snapshot: conformity dashboard
    DRAFT.md               -> the DRAFT v0.60 protocol itself (reference)
```

## The layers

| Layer | File | Role |
|---|---|---|
| **D.1 Conditions** | `1-Rules.md` | Every format, mandatory item, bonus, open point and ambiguity from the subject, each classified and marked done / partial / open. The problem, readable in about 60 seconds. |
| **D.2 Logic** | `2-Logic.md` | The logical contract: one BIOPGE block (Boundary, Inputs, Outputs, Process, Guarantees, Errors) per module, tracing back to the D.1 requirement IDs it covers. |
| **D.3 Embodiment** | `3-DebugLog.md` | The development journal: decisions, the refactor debrief, the debug phases and the issues found and resolved at review time. |
| **D.4 Overseer** | `4-Overseer.md` | Supervision snapshot: a conformity dashboard across D0-D4, with completion and conformity percentages and certain / sensed markers. |

## How to read it

Start from `1-Rules.md` for what the game must do,
cross-check `2-Logic.md` for how each module is meant to behave,
and read `3-DebugLog.md` for the history, the deviations from the plan and the open issues.

The user-facing documentation (build, run, configuration, architecture) lives in the root `README.md`.
