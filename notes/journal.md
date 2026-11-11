# Journal

One entry per work session, newest at the bottom, appended at `close`.
Each entry: what was done, decisions and why, problems, next step.

## 2026-11-11 — Session 1: plan and setup

**Done**
- Read the statement, the sample task sets, the Practice 1 simulator and
  the wiki pages on feasibility intervals, EDF and partitioning.
- Wrote and approved the plan (`plan.md`): structure, feasibility table,
  decision order, milestones M0–M8.
- Created the repo folder, `notes/`, `CLAUDE.md` and the `sync`/`close`
  session commands. Git configured (identity, Windows credential manager),
  remote `origin` on GitHub (private), first commit and push.
- Environment: Windows `.venv` from Anaconda Python 3.13.5 with pytest and
  matplotlib; `.vscode/settings.json` and `launch.json`.

**Decisions**
- Event-driven simulator: some samples have P ≈ 1.1 M, so stepping one unit
  at a time up to O_max + 2P would be too slow in Python.
- Exit 5 for invalid input, so it can't be confused with exit 2.
- Model classified per core after partitioning.
- No AI attribution line in commits, as in the thesis.
- Working method: the user types the code. Claude writes one file at a
  time in the chat, so every line is understood (oral defence). Simple
  code, no over-engineering.
- Python on Windows (Anaconda's interpreter), not WSL, as for the thesis
  scripts. Claude runs the venv from WSL through `.venv/Scripts/python.exe`.
- Git: Claude writes the commands, the user commits and pushes from VS Code
  (Git for Windows). `close` = tests, notes, commands. `sync` finds the
  previous session by the `notes: close session N` commit message, so
  `status.md` no longer stores a hash.
- `core.filemode false`: WSL git had committed the Windows-created files
  as executable (100755), which Git for Windows reported as changes.
- Dev notes and `.claude/` live in the repo (they travel with git) but are
  left out of the hand-in zip.

**Problems**
- First push: a stale GitHub login stored in Windows Credential Manager
  was rejected; erased it, and the browser login then worked.
- GitHub's EU IPs (140.82.121.x) timed out from the home network (Windows
  too) while other sites worked; the push went through later.
- PowerShell: a full path with spaces must be quoted (`& "C:\...\python.exe"`)
  or replaced by the relative `.venv\Scripts\python.exe`.

**Next**
- M1 code part: `__init__`, `__main__`, `exit_codes`, `model`,
  `taskset_io`, `cli` skeleton, `project` launcher, `test_parsing`.
