# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-23 (close of session 6)
- **Current milestone:** M7 — bonus Gantt visualisation (not started). M5 and M6 done: the program is functionally complete.
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** 130 passed (16 parsing, 18 analysis, 14 feasibility, 8 simulator, 13 schedulability, 9 partitioner, 12 cli, 40 custom: 39 `expected.csv` rows + 1 sample consistency check)

## Done

- M0–M4: plan and workflow, scaffold, analysis, schedulers and feasibility
  intervals, simulator and one-core decision (see `journal.md`).
- M5: `rtsched/partitioner.py`, multi-core flow in `cli.main`,
  `tests/test_partitioner.py`, multi-core tests in `test_cli.py`.
- M6: `tasksets/custom/` (12 task sets + `expected.csv`, 39 rows, every exit
  code 0–4), `scripts/run_all.py` (`--check` and samples table),
  `tests/test_custom.py`. Samples: 60 files × rm/dm/edf in 0.7 s; a sweep
  of 4,320 multi-core runs (scratch copy) had no crash, worst run 0.27 s.

## Code state

| Module | State |
|---|---|
| exit_codes | done: 0–4 from the statement, 5 = invalid input |
| model | done: `Task`, `Job`, `TaskSet` (classification) |
| taskset_io | done: `read_taskset`, `InvalidTaskFile` |
| cli | done: `-m 1` → whole set on one core; `-m > 1` → `partition` (None → 1), then `check_schedulability` per non-empty core in order, stop at the first code ≠ 0. Prints `core k (tau…): <verdict>: <reason>` |
| analysis | done: `ceil_div`, `hyperperiod`, `busy_period`, `s_n`, `response_times`, `liu_layland_bound` |
| schedulers | done: RM, DM, EDF priority keys, `get_scheduler` |
| feasibility | done: `check_supported`, `feasibility_interval` |
| simulator | done: `simulate(tasks, scheduler, start, end) -> Job | None` |
| schedulability | done: `check_schedulability(tasks, scheduler) -> (code, reason)` |
| partitioner | done: `sort_by_utilization` (du/iu, ties by index), `partition(tasks, cores, heuristic, order)`: FF/BF/WF/NF, capacity 1 (`Fraction`), ties to the lowest core, NF never goes back; cores returned in index order |
| scripts/run_all.py | done: `<folder>` table + counts; `--check <csv>` (exit 1 on a difference); `-H` for the heuristic (argparse `-h` = help) |
| visualization (bonus) | — |
| scripts/package.py | — |
| README.md, report | — |

## Next step

M7 (bonus), then M8:

1. M7: decide the design with the user first (plan §1: Gantt chart with
   deadline misses marked and releases shown; `--plot` extra flag;
   matplotlib in `requirements.txt`). The simulator would need to record
   the executed slices (task, job, start, end), e.g. an optional `trace`
   list argument, without changing its result. Check matplotlib is in the
   venv first.
2. M8: `README.md` (user guide; Python ≥ 3.10 because of `int | None` and
   `math.lcm`; commands `./project …` or `python -m rtsched …`,
   `python -m pytest -q`, `python scripts/run_all.py --check
   tasksets/custom/expected.csv`, `python scripts/run_all.py <samples
   folder>`; the teacher has no `.venv`), `scripts/package.py` (zip must
   include `tests/`, `tasksets/custom/`, `scripts/`), report
   (`report/main.tex`, ≤ 3 pages of description; results table from
   `run_all.py`; examples: system 47 under RM vs EDF, `full-utilization`
   FF vs WF, sample `asynchronous/arbitrary/taskset-1` classified as
   constrained).

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
- Plan target: M7–M8 by 5 Dec (M5–M6 met on 23 Nov, 4 days early).
- Network: GitHub's EU servers (140.82.121.x) are sometimes unreachable
  from the home network; if a push hangs, push from another network or
  retry later.
