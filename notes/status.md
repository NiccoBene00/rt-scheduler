# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-20 (close of session 5)
- **Current milestone:** M5 — partitioner + multiprocessor flow (not started). M4 done: the one-core program is complete.
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** 76 passed (16 parsing, 18 analysis, 14 feasibility, 8 simulator, 13 schedulability, 7 cli)

## Done

- M0: plan, notes, `sync`/`close` commands, GitHub repo.
- M1: Windows `.venv` (Anaconda Python 3.13.5), VS Code config,
  `rtsched/` package (`__init__`, `__main__`, `exit_codes`, `model`,
  `taskset_io`, `cli` skeleton), `project` launcher (staged as 100755),
  `tests/test_parsing.py`, `pytest.ini`.
- M2: `rtsched/analysis.py` and `tests/test_analysis.py`.
- M3: `rtsched/schedulers/` (base, rm, dm, edf, registry),
  `rtsched/feasibility.py`, `tests/test_feasibility.py`.
- M4: `rtsched/simulator.py`, `rtsched/schedulability.py`, one-core flow in
  `cli.main`, `tests/test_simulator.py`, `test_schedulability.py`,
  `test_cli.py`. Smoke run on all 60 samples × rm/dm/edf (from a scratch
  copy): no crash, every run < 2 s, RM/DM-schedulable ⇒ EDF-schedulable,
  RM = DM on implicit sets.

## Code state

| Module | State |
|---|---|
| exit_codes | done: 0–4 from the statement, 5 = invalid input |
| model | done: `Task` (frozen, `index` for ties, `utilization()` as `Fraction`, `release_time(k)`), `Job` (`release`, `remaining`, `deadline` property), `TaskSet` (`utilization`, `is_synchronous` = all offsets equal, `deadline_type`, `describe`) |
| taskset_io | done: `read_taskset`, `parse_line`, `InvalidTaskFile`; utf-8-sig, blank lines skipped; C > D accepted (analysis rejects it) |
| cli | one core done: `VERDICTS` table, `main` = read → `get_scheduler` → `check_schedulability` → print `<verdict>: <reason>` → return code. `-m > 1` returns 5 with "not implemented yet" (TODO M5) |
| analysis | done: all take `list[Task]`. `ceil_div`, `hyperperiod`, `busy_period` (Th. 40/58, `ValueError` if U > 1), `s_n` (Th. 45 / Cor. 46), `response_times` (Th. 29, `None` when w > D_i), `liu_layland_bound` (Th. 33). `s_n` and `response_times` need tasks in priority order |
| schedulers | done: `Scheduler` (`job_key`, `pick` = min key, `fixed_task_priority`), `FixedTaskPriority` (`task_key`, `sort_tasks`, job key = task key + release). RM (T, index), DM (D, index), EDF (abs. deadline, index, release). `get_scheduler(name)` |
| feasibility | done: `check_supported` (raises `Unsupported` for FTP + async + arbitrary), `feasibility_interval(tasks, scheduler) -> (start, end)` (calls `check_supported` first). Requires U ≤ 1 |
| simulator | done: `simulate(tasks, scheduler, start, end) -> Job | None`, event-driven (release / completion / deadline), releases only before `end`, jobs followed to completion, first miss by (deadline, index) |
| schedulability | done: `check_schedulability(tasks, scheduler) -> (code, reason)`: unsupported → 2; C > D or U > 1 → 3; EDF implicit → 0 (Cor. 54); FTP constrained → sync RTA (exact if sync, sufficient if async, Lemma 25); else simulate → 0/4 |
| partitioner | — |
| visualization (bonus) | — |
| report | — |

## Next step

M5, one file at a time (Claude writes in the chat, the user types):

1. Read plan §3 "Partitioner" and the statement's partitioning section
   (`../../project-description.pdf`) again before writing.
2. `rtsched/partitioner.py`: sort tasks by utilisation (`du` decreasing /
   `iu` increasing, ties by index), then FF / NF / BF / WF with capacity 1
   per core (U_core + U_i ≤ 1, exact `Fraction`). BF = eligible core with
   the highest load, WF = lowest, ties to the lowest core index; NF never
   returns to earlier cores. Returns the list of tasks per core, or None
   when a task fits nowhere (exit 1). Keep `Task.index` unchanged per core.
3. `tests/test_partitioner.py` (one case per heuristic where they differ).
4. `cli.main`: replace the `-m > 1` guard: partition (fail → 1), then
   `check_schedulability` per core in order, stop at the first core that
   is not 0; print which core. Decide with the user how to combine codes
   (e.g. core 1 unsupported, core 2 schedulable). Extend `test_cli.py`.
5. Then M6: custom task sets, `expected.csv`, `scripts/run_all.py`.

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
- Multiprocessor: which exit code when cores give different results (first
  failing core in order, per plan §3)? Confirm while writing M5.
- Plan target: M5–M6 by 27 Nov (M1–M4 met on 20 Nov).
- Network: GitHub's EU servers (140.82.121.x) are sometimes unreachable
  from the home network; if a push hangs, push from another network or
  retry later.
