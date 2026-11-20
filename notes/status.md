# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-20 (close of session 3)
- **Current milestone:** M3 — priority functions and `feasibility.py` (not started). M2 done.
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** 34 passed (16 `tests/test_parsing.py`, 18 `tests/test_analysis.py`)

## Done

- M0: plan, notes, `sync`/`close` commands, GitHub repo.
- M1: Windows `.venv` (Anaconda Python 3.13.5), VS Code config,
  `rtsched/` package (`__init__`, `__main__`, `exit_codes`, `model`,
  `taskset_io`, `cli` skeleton), `project` launcher (staged as 100755),
  `tests/test_parsing.py`, `pytest.ini`.
- M2: `rtsched/analysis.py` and `tests/test_analysis.py`.

## Code state

| Module | State |
|---|---|
| exit_codes | done: 0–4 from the statement, 5 = invalid input |
| model | done: `Task` (frozen, `index` for ties, `utilization()` as `Fraction`, `release_time(k)`), `Job` (`release`, `remaining`, `deadline` property), `TaskSet` (`utilization`, `is_synchronous` = all offsets equal, `deadline_type`, `describe`) |
| taskset_io | done: `read_taskset`, `parse_line`, `InvalidTaskFile`; utf-8-sig, blank lines skipped; C > D accepted (analysis rejects it) |
| cli | skeleton: argparse subclass exits 5 on errors, `add_help=False` + `--help` (since `-h` = heuristic), `positive_int` for `-m`; `main(argv)` returns the code; prints the classification and returns 0 (TODO M3–M5) |
| analysis | done: all functions take `list[Task]`. `ceil_div` (integer ceiling), `hyperperiod` (`math.lcm`), `busy_period` (Th. 40/58, from Σ C_i, `ValueError` if U > 1), `s_n` (Th. 45 / Cor. 46, tasks in priority order), `response_times` (Th. 29, Eq. 3.1–3.2, from w_0 = C_i, `None` when w > D_i; tasks in priority order), `liu_layland_bound` (Th. 33, float, report only) |
| schedulers (rm, dm, edf) | — |
| feasibility, schedulability | — |
| simulator | — |
| partitioner | — |
| visualization (bonus) | — |
| report | — |

## Next step

M3, one file at a time (Claude writes in the chat, the user types):

1. `rtsched/schedulers/` (`base.py`, `rm.py`, `dm.py`, `edf.py`): priority
   keys from plan §3: RM (T, index), DM (D, index), EDF (absolute deadline,
   index, release); jobs of one task FIFO. FTP schedulers also need a
   function that sorts a `list[Task]` in decreasing priority, for `s_n` and
   `response_times`.
2. `rtsched/feasibility.py`: the decision table of plan §3 → interval
   `(start, end)` or `Unsupported(reason)`; handles the shift for
   synchronous sets with equal non-zero offsets.
3. `tests/test_feasibility.py`: system 47 under RM → [0, 244); system 110
   given in the guide's order, sorted by DM → RTA `[1, 3, 4, 14]`.
4. Then M4: simulator and `schedulability.py`.

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
- Behind the plan's target (M1–M4 by 20 Nov): M2 done on 20 Nov; M3–M4
  must catch up before the M5–M6 target of 27 Nov.
- Network: GitHub's EU servers (140.82.121.x) are sometimes unreachable
  from the home network; if a push hangs, push from another network or
  retry later.
