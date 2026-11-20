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

## 2026-11-16 — Session 2: M1 scaffold

**Done**
- Wrote M1 file by file (Claude in the chat, user typing in VS Code):
  `rtsched/__init__.py`, `__main__.py`, `exit_codes.py`, `model.py`,
  `taskset_io.py`, `cli.py` (skeleton), `project` launcher,
  `tests/test_parsing.py`. 16 tests pass.
- Checked the CLI by hand: valid file → 0, bad `-a` and missing file → 5,
  `--help` works.

**Decisions**
- `Fraction` for utilisations: exact, so `U <= 1` is never wrong by a
  rounding error at U = 1.
- `Task.index` (line order, blank lines not counted) is the RM/DM tie-break,
  kept on every core after partitioning.
- Synchronous = all offsets equal (not necessarily 0); the shift is handled
  in `feasibility.py`.
- C > D and U > 1 are valid input; the analysis rejects them (exit 3), not
  the parser (exit 5).
- argparse subclass whose `error()` exits 5 instead of 2; `add_help=False`
  and a manual `--help`, because the statement uses `-h` for the heuristic.
- `main(argv)` returns the exit code instead of exiting, so tests can call
  it; `__main__.py` and `project` call `sys.exit(main())`.
- `pytest.ini` with `pythonpath = .` so plain `pytest` (VS Code Testing
  panel) finds `rtsched`.

**Problems**
- `sync` was first called from the course folder, where the skill is not
  loaded; sessions must open in `rt-scheduler/`.
- `pytest.ini` was not created yet at close (tests pass through
  `python -m pytest`).

**Next**
- M2: `analysis.py` (hyperperiod, busy period, S_n, RTA) and
  `tests/test_analysis.py`.

## 2026-11-20 — Session 3: M2 analysis

**Done**
- Wrote `rtsched/analysis.py` function by function (Claude in the chat,
  user typing in VS Code): `ceil_div`, `hyperperiod`, `busy_period`,
  `s_n`, `response_times`, `liu_layland_bound`. Each was checked by hand in
  the terminal before the next one.
- Wrote `tests/test_analysis.py` (18 tests) against the curriculum guide:
  system 30 (r_3 = 15), system 47 (S_3 = 4, P = 240 → [0, 244)), system
  108 under RM and system 110 under DM (both `[1, 3, 4, 14]`). 34 tests pass.
- `pytest.ini` turned out to be committed already.

**Decisions**
- Analysis functions take `list[Task]`, not `TaskSet`, so they also run on
  one core's tasks after partitioning.
- `ceil_div(a, b) = -(-a // b)`: exact integer ceiling, no float division.
- `busy_period` raises `ValueError` when U > 1: the loop is only bounded
  (by P) when U ≤ 1, so misuse becomes an error, not an infinite loop.
- `response_times` follows the guide's Eq. 3.2: start from w_0 = C_i, stop
  at the fixed point or when w > D_i, and return `None` for that task
  (exact value not needed, Th. 29 only needs r_i ≤ D_i).
- `s_n` and `response_times` expect tasks already sorted by decreasing
  priority; sorting belongs to the scheduler (M3).
- `liu_layland_bound` returns a float (2^(1/n) is irrational); it is only
  a sufficient test, kept for the report, not used for exit codes.
- Theorem numbers checked in the guide: RTA = Th. 29, LL = Th. 33,
  [0, S_n + P) = Th. 45 / Cor. 46.

**Next**
- M3: scheduler priority functions, `feasibility.py`, `tests/test_feasibility.py`.

## 2026-11-20 — Session 4: M3 schedulers and feasibility intervals

**Done**
- Wrote `rtsched/schedulers/` (`base.py`, `rm.py`, `dm.py`, `edf.py`,
  `__init__.py` with `get_scheduler`), `rtsched/feasibility.py` and
  `tests/test_feasibility.py` (14 tests). 48 tests pass.
- Gave the design and code of `simulator.py` in the chat (not typed yet).

**Decisions**
- Priority as a key tuple, smallest = highest: one `min` for every
  scheduler, ties visible in the key, keys unique (task index + release),
  so `pick` is deterministic whatever the list order.
- `FixedTaskPriority` subclasses define only `task_key`; the job key is
  task key + release (FIFO between jobs of one task, for arbitrary
  deadlines) and `sort_tasks` gives the order `s_n` / `response_times` need.
  EDF subclasses `Scheduler` directly (priority per job, no task order).
- `feasibility.py` returns only the interval, for every supported
  combination; the no-simulation shortcuts go in `schedulability.py`.
- Sync FTP constrained: [0, min(D_max, λ_n)), because the statement asks
  for the smallest interval and both Cor. 32 and Th. 40 apply.
- `Unsupported` is an exception with the reason; the CLI will turn it into
  exit 2.
- Theorem numbers checked in the guide: RM optimality Th. 28, DM Th. 35,
  EDF Def. 12 and Th. 52, [0, L) is Cor. 59 (Th. 58 is the idle-point
  property).

**Problems**
- Claude's expected interval for system 47 under RM was wrong (244): the
  guide's 244 uses the order τ1 ≻ τ2 ≻ τ3, while RM gives τ1 ≻ τ3 ≻ τ2,
  so S_n = 16 and the interval is [0, 256). The code was right; the test
  uses 256 and explains why.
- Claude miscounted the expected number of tests in session 3 (37 instead
  of 34); counts are now checked by running the tests.

**Next**
- M4: type `simulator.py`, then `test_simulator.py`, `schedulability.py`
  and the one-core CLI flow.
