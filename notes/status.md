# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-20 (close of session 4)
- **Current milestone:** M4 — simulator + `schedulability.py` (not started in code). M3 done.
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** 48 passed (16 `test_parsing`, 18 `test_analysis`, 14 `test_feasibility`)

## Done

- M0: plan, notes, `sync`/`close` commands, GitHub repo.
- M1: Windows `.venv` (Anaconda Python 3.13.5), VS Code config,
  `rtsched/` package (`__init__`, `__main__`, `exit_codes`, `model`,
  `taskset_io`, `cli` skeleton), `project` launcher (staged as 100755),
  `tests/test_parsing.py`, `pytest.ini`.
- M2: `rtsched/analysis.py` and `tests/test_analysis.py`.
- M3: `rtsched/schedulers/` (base, rm, dm, edf, registry),
  `rtsched/feasibility.py`, `tests/test_feasibility.py`.

## Code state

| Module | State |
|---|---|
| exit_codes | done: 0–4 from the statement, 5 = invalid input |
| model | done: `Task` (frozen, `index` for ties, `utilization()` as `Fraction`, `release_time(k)`), `Job` (`release`, `remaining`, `deadline` property), `TaskSet` (`utilization`, `is_synchronous` = all offsets equal, `deadline_type`, `describe`) |
| taskset_io | done: `read_taskset`, `parse_line`, `InvalidTaskFile`; utf-8-sig, blank lines skipped; C > D accepted (analysis rejects it) |
| cli | skeleton: argparse subclass exits 5 on errors, `add_help=False` + `--help` (since `-h` = heuristic), `positive_int` for `-m`; `main(argv)` returns the code; prints the classification and returns 0 (TODO M4–M5) |
| analysis | done: all take `list[Task]`. `ceil_div`, `hyperperiod`, `busy_period` (Th. 40/58, `ValueError` if U > 1), `s_n` (Th. 45 / Cor. 46), `response_times` (Th. 29, `None` when w > D_i), `liu_layland_bound` (Th. 33). `s_n` and `response_times` need tasks in priority order |
| schedulers | done: `Scheduler` (`job_key`, `pick` = min key, `fixed_task_priority`), `FixedTaskPriority` (`task_key`, `sort_tasks`, job key = task key + release → FIFO per task). RM (T, index), DM (D, index), EDF (abs. deadline, index, release). `get_scheduler(name)` / `SCHEDULERS` in `__init__` |
| feasibility | done: `feasibility_interval(tasks, scheduler) -> (start, end)`, `Unsupported` (FTP + async + arbitrary). Sync FTP constrained [0, min(D_max, λ_n)), sync FTP arbitrary [0, λ_n), sync EDF [0, L) (Cor. 59), async FTP [0, S_n + P) with RM/DM order, async EDF [0, O_max + 2P); sync shifted by the common offset. Requires U ≤ 1 |
| simulator | designed, code given in chat (session 4), not typed yet |
| schedulability | — |
| partitioner | — |
| visualization (bonus) | — |
| report | — |

## Next step

M4, one file at a time:

1. `rtsched/simulator.py`: the code was given in the chat at the end of
   session 4. Ask Claude to repeat it if needed. Design:
   `simulate(tasks, scheduler, start, end) -> Job | None` (first missed job).
   Loop: (1) misses = ready jobs with deadline ≤ t → return the min by
   (deadline, index); (2) release jobs with next_release == t < end;
   (3) idle → jump to the next release < end or return None; (4) run
   `scheduler.pick(ready)` until min(t + remaining, next release < end,
   ready deadlines); subtract; remove when remaining == 0.
   Check: system 30 under RM on [0, 15) → None; with D_3 = 14 on [0, 14) →
   the job of τ3 (index 2, release 0, deadline 14, remaining 1).
2. `tests/test_simulator.py`.
3. `rtsched/schedulability.py` (plan §3 decision order). `feasibility_interval`
   raises `ValueError` from `busy_period` when U > 1, so check C > D / U > 1
   (exit 3) before computing it; `Unsupported` only occurs for async sets,
   which never call `busy_period`, so "unsupported first" still holds.
   Shortcuts: sync FTP constrained → RTA (exact, 0 or 3); async FTP
   constrained → sync RTA passes → 0; EDF implicit → U ≤ 1 → 0.
4. Wire `cli.main` for one core (print the reason for exit 2, the missed
   job for exit 4), then `tests/test_cli.py`.

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
- Behind the plan's target (M1–M4 by 20 Nov): M3 done on 20 Nov; M4 must
  be done quickly to keep the M5–M6 target of 27 Nov.
- Network: GitHub's EU servers (140.82.121.x) are sometimes unreachable
  from the home network; if a push hangs, push from another network or
  retry later.
