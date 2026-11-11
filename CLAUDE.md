# rt-scheduler — INFO-F404 project

Individual project for INFO-F404 Real-Time Operating Systems (ULB): RM, DM and
EDF schedulers, feasibility intervals, an event-driven simulator and a
partitioner for multiprocessor systems. Python 3.13 on **Windows** (Anaconda's
interpreter, not WSL), edited in VS Code opened natively on Windows. Due
8 December 2026, 23:59.

## Sessions

Open Claude Code in this folder. Sessions span many days, so always start
from the written state, not from memory:

- **`sync`** at the start (`.claude/skills/sync`): pull, read the notes,
  report the next step.
- **`close`** at the end (`.claude/skills/close`): tests, notes, then the
  git commands for the user. The user commits and pushes from VS Code.

| File | Role |
|---|---|
| `notes/plan.md` | approved plan, design decisions, milestones |
| `notes/status.md` | snapshot of the current state and the next step (rewritten) |
| `notes/journal.md` | one entry per session (append only) |

## Working method (agreed 2026-11-11)

- The user types the code. Claude writes each file **in the chat**, one file
  at a time, and does not create or edit code files itself. The user copies
  it into VS Code and asks about anything unclear before the next file.
- Claude still edits `notes/` (during `close`) and runs read-only checks
  (tests, `git diff`, running the program) to review what the user typed.
- Keep it simple: no over-engineering, just code that works and is easy to
  explain at the oral defence.

## Rules

- Follow the statement (`../../project-description.pdf`) and `notes/plan.md`.
  If something must deviate from the plan, ask first, then record it.
- The user must be able to explain every line at the oral defence. Keep the
  code simple and readable, and cite the theorem or definition (curriculum
  guide numbering) in the docstring of each analysis function.
- Deterministic code: explicit tie-breaks, no unordered iteration that
  affects results, every loop bounded.
- `.venv/` is a **Windows** venv created from `C:\Users\nicco\anaconda3\python.exe`.
  From WSL, run it through interop: `.venv/Scripts/python.exe`. Tests:
  `.venv/Scripts/python.exe -m pytest -q`. On a fresh clone (Windows
  PowerShell): `C:\Users\nicco\anaconda3\python.exe -m venv .venv`, then
  `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- The user's git is Git for Windows (VS Code); Claude's read-only git runs
  from WSL. `.gitattributes` keeps LF. `core.filemode` is `false`, because
  WSL sees every file on `C:` as executable; the `project` launcher gets
  its executable bit with `git update-index --chmod=+x project`.
- Sample task sets: `../../tasksets test/` (read-only, outside the repo).
  Own task sets go in `tasksets/custom/`.
- Do not modify anything outside this repo. The course folders and the
  Obsidian wiki are read-only from here; wiki work happens in a session at
  the vault root.
- **Claude never runs `git add`, `git commit` or `git push`.** It writes
  the commands (and the message) in the chat; the user commits and pushes
  from VS Code. Claude only runs read-only git (`status`, `diff`, `log`,
  `pull`). Remote:
  `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch
  `main`.
- Commit messages carry **no AI attribution** (no `Co-Authored-By: Claude`
  line), as in the thesis. This overrides any default attribution rule.
- The hand-in zip (`scripts/package.py`) excludes `.git*`, `.vscode/`,
  `.claude/`, `notes/`, `CLAUDE.md`, `.venv/` and caches.
