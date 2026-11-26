# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-26 (close of session 7)
- **Current milestone:** M8 — README, `package.py`, report (not started). M7 done: program and bonus complete.
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** 134 passed (16 parsing, 18 analysis, 14 feasibility, 8 simulator, 13 schedulability, 9 partitioner, 16 cli, 40 custom)

## Done

- M0–M6: see `journal.md` (scaffold, analysis, schedulers, feasibility
  intervals, simulator, decision order, partitioner, custom task sets,
  `run_all.py`).
- M7: `simulate(..., trace=None)` records (task index, release, start, end)
  stretches; `rtsched/visualization.py` (`drawing_window`, `plot_core`);
  `--plot FILE` in the CLI (`gantt_path`); 4 plot tests in `test_cli.py`.
  Charts checked by eye: system 30-d14 (miss at 14), system 47 under RM,
  arbitrary-two-active-jobs (FIFO visible), overload (U > 1, [0, 200)),
  sample `asynchronous/constrained/taskset-5` (200-unit window, 0.35 s).

## Code state

| Module | State |
|---|---|
| exit_codes, model, taskset_io | done |
| cli | done: one core or `partition`, `check_schedulability` per core, stop at the first code ≠ 0; `--plot FILE` (lazy import of `visualization`, not for exit 2 cores) |
| analysis, schedulers, feasibility | done |
| simulator | done: `simulate(tasks, scheduler, start, end, trace=None) -> Job | None` |
| schedulability, partitioner | done |
| visualization | done: window = feasibility interval cut to `MAX_LENGTH` = 200 (`ValueError` → [0, 200)); bars with black outline, release triangles, red cross at the miss; margins 2 %; title with window and status |
| scripts/run_all.py | done |
| scripts/package.py | — |
| README.md | — |
| report/main.tex | — |

## Next step

M8, in this order:

1. `README.md` (user guide, also needed in the report):
   - Python ≥ 3.10 (`int | None`, `math.lcm`); stdlib only for the program
     and `run_all.py`; `pytest` for the tests; `matplotlib` only for
     `--plot`. The teacher has no `.venv`: `python -m pip install -r
     requirements.txt`.
   - Commands: `./project <file> -a edf|rm|dm [-m N] [-h ff|bf|nf|wf]
     [-s du|iu] [--plot FILE]` or `python -m rtsched …`; exit codes 0–5;
     `python -m pytest -q`; `python scripts/run_all.py --check
     tasksets/custom/expected.csv`; `python scripts/run_all.py <samples
     folder>` (`-m`, `-H`, `-s`).
2. `scripts/package.py`: zip of the repo without `.git*`, `.vscode/`,
   `.claude/`, `notes/`, `CLAUDE.md`, `.venv/`, caches, `*.png` outside
   `report/`; must include `tests/`, `tasksets/custom/`, `scripts/`,
   `report/` PDF. Check the zip content and that the project runs from an
   unzipped copy (scratchpad).
3. `report/main.tex` (≤ 3 pages of description + user guide + extras +
   justification of choices): feasibility table with theorem numbers,
   decision order, simulator design, partitioner, `-m 1` choice, exit 5,
   per-core classification; results table from `run_all.py`; figures from
   `--plot` (system 30-d14, system 47 RM vs EDF, `full-utilization` FF vs
   WF); observations from the session 6 journal entry. Compile with
   latexmk into the scratchpad (vault `CLAUDE.md`).
4. Ask the user who writes the README and report prose (the working method
   covers code; agree it before starting).

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
- Plan target: M8 by 5 Dec (M7 met on 26 Nov).
- Network: GitHub's EU servers (140.82.121.x) are sometimes unreachable
  from the home network; if a push hangs, push from another network or
  retry later.
