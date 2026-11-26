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

## 2026-11-20 — Session 5: M4 simulator and one-core program

**Done**
- `rtsched/simulator.py`, `tests/test_simulator.py` (8 tests).
- `feasibility.check_supported` split out of `feasibility_interval`.
- `rtsched/schedulability.py`, `tests/test_schedulability.py` (13 tests).
- One-core flow in `cli.main` (`VERDICTS`, `-m > 1` guard until M5),
  `tests/test_cli.py` (7 tests). 76 tests pass.
- Smoke run of the CLI on all 60 samples × rm/dm/edf, from a scratch copy:
  no crash, every run < 2 s, every RM/DM-schedulable set is
  EDF-schedulable, RM = DM on implicit sets. Checked by hand:
  `asynchronous/constrained/taskset-1` → 0 by simulation on [0, 350),
  `taskset-2` → 4.

**Decisions**
- Event-driven simulator: next event = min(completion of the running job,
  next release before `end`, deadlines of ready jobs); misses checked
  before releases, so finishing exactly at the deadline meets it. Returns
  the first missed `Job` (for messages and the bonus Gantt chart).
- `check_supported` runs first in `schedulability.py`, before the C > D /
  U > 1 check, so the plan's order holds and `busy_period` never sees
  U > 1.
- Step 3 of the decision order: EDF implicit → 0 (Cor. 54); FTP
  constrained → synchronous RTA, exact for synchronous sets (Th. 29),
  sufficient for asynchronous sets (Lemma 25, critical instant), else
  simulation.
- `check_schedulability` returns `(code, reason)`; the CLI prints one line
  `<verdict>: <reason>`, tasks numbered from 1 (τ1 = first task).
- `-m > 1` returns 5 until M5, so a multi-core run is never reported as
  schedulable without being checked.

**Problems**
- A leftover nested `if scheduler.fixed_task_priority:` in
  `feasibility.py` after the refactor; removed.
- Claude's sample command used a placeholder (`<a file>`); give real paths.
- Running the Windows venv from WSL on a scratch copy needs Windows paths
  (`wslpath -w`).

**Next**
- M5: `partitioner.py`, `test_partitioner.py`, multi-core flow in the CLI.

## 2026-11-23 — Session 6: M5 partitioner, M6 task set checks

**Done**
- M5: `rtsched/partitioner.py`, `tests/test_partitioner.py` (9 tests),
  multi-core flow in `cli.main` and 5 multi-core CLI tests. Committed
  during the session (`Add partitioner and multi-core flow`).
- M6: `tasksets/custom/` (12 task sets, `expected.csv` with 39 rows),
  `scripts/run_all.py`, `tests/test_custom.py`. 130 tests pass.
- Checks on a scratch copy before giving each file: all 60 samples ×
  rm/dm/edf × 2–4 cores × 4 heuristics × 2 orders (4,320 runs), no crash,
  worst run 0.27 s; samples table in 0.7 s.

**Decisions**
- Heuristics as in the guide §7.1.1; capacity 1 per core (statement), not
  RM's ln 2 bin size, because each core is then checked exactly. Ties to
  the lowest core; NF never goes back (fails past the last core).
- `-m 1` does not partition (user's choice, option A): U > 1 on one core
  stays exit 3, and the one-core behaviour of M4 is unchanged.
- Cores checked in order, the first code ≠ 0 is the exit code; empty cores
  skipped; one output line per core.
- Custom task sets with hand-derived codes, because the course samples have
  no expected answers; the samples are only checked for consistency (EDF
  schedules whatever RM/DM schedule, Th. 52).
- All paths are relative (to the test file, or given as arguments), so the
  teacher can run everything; the sample test is skipped when the folder is
  missing.
- Working-method exception (user's choice): Claude created the data files
  in `tasksets/custom/` itself; the user still types all code.

**Problems**
- Two of Claude's hand-derived expected codes were wrong (caught by the
  check before the files were handed over): `edf-constrained-miss` with
  `-m 2 ff` is 4, not 0 (FF packs U = 1 on one core), and `next-fit-fails`
  with `ff iu` is 1, not 0 (the iu order leaves 0.6 last). The code was
  right; the CSV uses the correct values.
- The user was unsure what M6 was for; explained the custom sets as an
  answer key the samples lack.

**Observations for the report**
- Samples are consistent with the theory: EDF never worse than RM/DM, DM
  never worse than RM on constrained sets.
- `asynchronous/arbitrary/taskset-1` has D ≤ T for both tasks, so it is
  classified as constrained (most specific type) and simulated (0), not
  unsupported.
- `asynchronous/constrained/taskset-2`: 4 under RM on one core, 0 with
  `-m 2 -h wf`.

**Next**
- M7: bonus Gantt chart (design first), then M8: README, `package.py`,
  report.

## 2026-11-26 — Session 7: M7 Gantt chart bonus

**Done**
- `simulate` got an optional `trace` list; `rtsched/visualization.py`
  (`drawing_window`, `plot_core`); `--plot FILE` and `gantt_path` in the
  CLI; 4 plot tests. 134 tests pass. Committed and pushed during the
  session (`Add Gantt chart bonus (--plot)`).
- Charts rendered on a scratch copy and checked by eye before the file
  was given; the user checked system 30-d14 and `full-utilization` with
  `-m 2 -h wf`.

**Decisions**
- With `--plot`, cores decided without simulation (RTA, Cor. 54) are also
  simulated, only for the chart: otherwise most sets (all implicit ones)
  would never get a chart, and the chart then shows the analysis result
  (e.g. τ3 finishing at r_3 = 15). The verdict still comes from
  `check_schedulability`; unsupported cores get no chart (no interval,
  "terminate early").
- `trace` as an optional list argument filled by the simulator, so
  `simulate` keeps its return value and no caller changes.
- Window = feasibility interval cut to 200 units; [0, 200) when U > 1
  (`busy_period` raises `ValueError`). A miss ends the chart at the missed
  deadline.
- PNG file, `Agg` backend (no window), so it works headless and gives
  report figures; one file per core (`FILE-coreK.png`).
- matplotlib imported inside the `--plot` branch, so the program runs
  without it.
- Thin black outline on each stretch, so two jobs of one task back to back
  are visible (arbitrary deadlines).

**Problems**
- The user asked to push M6, which was already pushed at the session 6
  close; clarified that the open work was M7.

**Next**
- M8: README, `package.py`, report. Agree first who writes the prose.
