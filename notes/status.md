# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-16 (close of session 2)
- **Current milestone:** M2 — `analysis.py` (not started). M1 done.
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** 16 passed (`tests/test_parsing.py`)

## Done

- M0: plan, notes, `sync`/`close` commands, GitHub repo.
- M1: Windows `.venv` (Anaconda Python 3.13.5), VS Code config,
  `rtsched/` package (`__init__`, `__main__`, `exit_codes`, `model`,
  `taskset_io`, `cli` skeleton), `project` launcher (staged as 100755),
  `tests/test_parsing.py`.

## Code state

| Module | State |
|---|---|
| exit_codes | done: 0–4 from the statement, 5 = invalid input |
| model | done: `Task` (frozen, `index` for ties, `utilization()` as `Fraction`, `release_time(k)`), `Job` (`release`, `remaining`, `deadline` property), `TaskSet` (`utilization`, `is_synchronous` = all offsets equal, `deadline_type`, `describe`) |
| taskset_io | done: `read_taskset`, `parse_line`, `InvalidTaskFile`; utf-8-sig, blank lines skipped; C > D accepted (analysis rejects it) |
| cli | skeleton: argparse subclass exits 5 on errors, `add_help=False` + `--help` (since `-h` = heuristic), `positive_int` for `-m`; `main(argv)` returns the code; prints the classification and returns 0 (TODO M3–M5) |
| analysis | — |
| schedulers (rm, dm, edf) | — |
| feasibility, schedulability | — |
| simulator | — |
| partitioner | — |
| visualization (bonus) | — |
| report | — |

## Next step

1. Check that `pytest.ini` exists in the repo root (it was missing at
   close: `[pytest]`, `testpaths = tests`, `pythonpath = .`). Tests pass
   anyway with `python -m pytest`.
2. M2: `rtsched/analysis.py`, one function at a time, each with the theorem
   in its docstring:
   - `hyperperiod(tasks)`: P = lcm of the periods.
   - `busy_period(tasks)`: smallest positive fixed point of
     w = Σ ⌈w/T_i⌉ C_i from w0 = Σ C_i (λ_n for FTP, L for EDF; Th. 40, 58).
     Only called when U ≤ 1, so it terminates.
   - `s_n(tasks)` for tasks in decreasing priority order: S_1 = O_1,
     S_i = O_i + ⌈(S_{i-1} − O_i)^+ / T_i⌉ T_i (Th. 45).
   - `response_times(tasks)` (RTA, tasks in priority order, constrained
     deadlines): R_i = C_i + Σ_{j<i} ⌈R_i/T_j⌉ C_j, stop when R_i > D_i.
   - `liu_layland_bound(n)`: n(2^{1/n} − 1) (optional, for the report).
   Then `tests/test_analysis.py` against the curriculum guide's examples
   (system 47: S_3 = 4, P = 240 → [0, 244); systems 108–110 for RTA).
3. Then M3: schedulers (priority functions) and `feasibility.py`.

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
- Behind the plan's target (M1–M4 by 20 Nov): M1 done on 16 Nov.
- Network: GitHub's EU servers (140.82.121.x) are sometimes unreachable
  from the home network; if a push hangs, push from another network or
  retry later.
