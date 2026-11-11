# rt-scheduler — INFO-F404 project

Individual project for INFO-F404 Real-Time Operating Systems (ULB): RM, DM and
EDF schedulers, feasibility intervals, an event-driven simulator and a
partitioner for multiprocessor systems. Python 3.12, edited in VS Code. Due
8 December 2026, 23:59.

## Sessions

Open Claude Code in this folder. Sessions span many days, so always start
from the written state, not from memory:

- **`sync`** at the start (`.claude/skills/sync`): pull, read the notes,
  report the next step.
- **`close`** at the end (`.claude/skills/close`): tests, notes, commit. The
  user pushes.

| File | Role |
|---|---|
| `notes/plan.md` | approved plan, design decisions, milestones |
| `notes/status.md` | snapshot of the current state and the next step (rewritten) |
| `notes/journal.md` | one entry per session (append only) |

## Rules

- Follow the statement (`../../project-description.pdf`) and `notes/plan.md`.
  If something must deviate from the plan, ask first, then record it.
- The user must be able to explain every line at the oral defence. Keep the
  code simple and readable, and cite the theorem or definition (curriculum
  guide numbering) in the docstring of each analysis function.
- Deterministic code: explicit tie-breaks, no unordered iteration that
  affects results, every loop bounded.
- Run Python through `.venv/bin/python`. Tests: `.venv/bin/python -m pytest -q`.
- Sample task sets: `../../tasksets test/` (read-only, outside the repo).
  Own task sets go in `tasksets/custom/`.
- Do not modify anything outside this repo. The course folders and the
  Obsidian wiki are read-only from here; wiki work happens in a session at
  the vault root.
- Commit only during `close` or when asked; never push. Remote:
  `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch
  `main`.
- Commit messages carry **no AI attribution** (no `Co-Authored-By: Claude`
  line), as in the thesis. This overrides any default attribution rule.
- The hand-in zip (`scripts/package.py`) excludes `.git*`, `.vscode/`,
  `.claude/`, `notes/`, `CLAUDE.md`, `.venv/` and caches.
