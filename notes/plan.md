# Plan — INFO-F404 scheduler simulator

Approved 2026-11-11. Deadline: zip on the UV by **8 December 2026, 23:59**;
individual oral defence in the week of 14 December.
Statement: `../../project-description.pdf` (relative to this repo root).

This file holds the plan and the design decisions. When a decision changes,
edit it here and record the reason in `journal.md`. The current state lives
in `status.md`.

## 1. Requirements from the statement

- RM, DM and EDF schedulers. Each one has a **feasibility interval** function
  and a **priority** function (highest-priority job of a set).
- The smallest feasibility interval for every combination up to asynchronous
  arbitrary deadlines; unsupported combinations print a meaningful error and
  stop (exit 2).
- Decide schedulability without simulation when possible; otherwise simulate
  each core up to its feasibility interval or the first deadline miss.
- Arbitrary deadlines: several jobs of the same task can be active at once.
- Partitioner: FF, NF, BF, WF × increasing or decreasing utilisation; fails
  if U_π > 1 on some core (exit 1).
- CLI: `./project <task_file> -a edf|rm|dm [-m <#cores>] [-h ff|bf|nf|wf] [-s du|iu]`,
  defaults `-m 1 -h ff -s du`.
- Exit codes: 0 schedulable, 1 partitioning failed, 2 unsupported
  combination, 3 not schedulable (no simulation), 4 not schedulable
  (simulation). Deterministic, always terminates.
- Report (PDF): description ≤ 3 pages, user guide, extras, justification of
  choices.
- Bonus: Gantt visualisation with deadline misses marked and job releases
  shown.

## 2. Repository structure

```
rt-scheduler/
├── project                  launcher (python3 shebang) → rtsched.cli.main
├── README.md                user guide
├── requirements.txt         matplotlib (bonus), pytest
├── CLAUDE.md                instructions for Claude Code sessions
├── .gitignore / .gitattributes
├── .claude/skills/          sync and close session commands (not in the zip)
├── .vscode/                 launch.json, settings.json (not in the zip)
├── notes/                   plan.md, status.md, journal.md (not in the zip)
├── rtsched/
│   ├── __init__.py, __main__.py
│   ├── cli.py               argparse, orchestration, exit code
│   ├── exit_codes.py
│   ├── taskset_io.py        parse offset;wcet;deadline;period
│   ├── model.py             Task, TaskSet, Job, classification
│   ├── analysis.py          U, P, busy period, S_n, RTA, LL bound
│   ├── schedulers/          base.py, rm.py, dm.py, edf.py
│   ├── feasibility.py       decision table → interval or Unsupported(reason)
│   ├── schedulability.py    tests without simulation, then simulation
│   ├── simulator.py         event-driven simulator
│   ├── partitioner.py       FF/NF/BF/WF × du/iu
│   └── visualization.py     bonus Gantt chart
├── tasksets/custom/         own task sets + expected.csv
├── tests/                   test_parsing, test_analysis, test_feasibility,
│                            test_simulator, test_schedulability,
│                            test_partitioner, test_cli, test_custom
├── scripts/                 run_all.py (results table), package.py (zip)
└── report/                  main.tex, figures/
```

Sample task sets stay in `../../tasksets test/` (outside the repo). Tests
that use them are skipped when the folder is not found.

## 3. Design

### Priorities and ties (deterministic)

- RM: (T, task index). DM: (D, task index). EDF: (absolute deadline, task
  index, release).
- Jobs of the same task run oldest first (FIFO): this covers arbitrary
  deadlines.

### Feasibility intervals (per core)

| Task set | RM / DM (FTP) | EDF (FJP) |
|---|---|---|
| sync implicit | RTA, exact, no simulation | U ≤ 1 → 0, no simulation |
| sync constrained | RTA, exact, no simulation | simulate [0, L) |
| sync arbitrary | simulate [0, λ_n) | simulate [0, L) |
| async implicit | sync RTA passes → 0; else simulate [0, S_n + P) | U ≤ 1 → 0, no simulation |
| async constrained | sync RTA passes → 0; else simulate [0, S_n + P) | simulate [0, O_max + 2P) |
| async arbitrary | **unsupported → exit 2** | simulate [0, O_max + 2P) |

λ_n and L: smallest positive fixed point of w = Σ ⌈w / T_i⌉ C_i, starting
from Σ C_i. S_1 = O_1, S_i = O_i + ⌈(S_{i-1} − O_i)^+ / T_i⌉ T_i in
decreasing priority order. Theory: guide Th. 29 (RTA), Cor. 32, Th. 33 (LL),
Th. 39–40, 44–45, Cor. 46, 54, 58, Cor. 59, 61–63.

`feasibility.py` returns the interval for every supported combination (the
statement's "feasibility interval" feature); the shortcuts without
simulation in the table above belong to `schedulability.py`. Sync FTP with
constrained deadlines uses [0, min(D_max, λ_n)) (Cor. 32 and Th. 40 are
both feasibility intervals, the smaller one is kept). Sync sets with every
offset = O > 0 get the interval shifted by O.

### Decision order (`schedulability.py`)

1. Unsupported combination → 2.
2. Some C_i > D_i, or U > 1 → 3.
3. An exact or sufficient test applies → 0 (or 3 when the test is exact).
4. Otherwise simulate → 0 or 4.

Step 1 is `feasibility.check_supported`, run before step 2 so that
`busy_period` never sees U > 1. Step 3: EDF implicit → 0 (Cor. 54); FTP
constrained → synchronous RTA (Th. 29), exact for synchronous sets (0 or
3), sufficient for asynchronous ones (Lemma 25: passing → 0, failing →
simulate). The CLI prints one line `<verdict>: <reason>` (tasks numbered
from 1, τ1 = first line).

### Simulator

Event-driven: jump to the next release, completion or deadline instead of
stepping one unit at a time (some samples have P ≈ 1.1 M). Jobs released in
the interval are followed until they complete, so a deadline after the end
of the interval is still checked. Stops at the first miss.

### Partitioner

Capacity 1 per core (the statement). BF = eligible core with the highest
load, WF = lowest load, ties to the lowest core index. NF never returns to
earlier cores. Cores are then checked in order; the run stops at the first
core that is not schedulable, and its code is the exit code. `-m 1` does not
go through the partitioner (the whole set is the core), so U > 1 on one core
stays exit 3. Empty cores are skipped. Output: one line per core,
`core k (tau…): <verdict>: <reason>`.

### Checking against task files

`tasksets/custom/`: own small task sets whose exit code is derived by hand
or from the guide, listed in `expected.csv`
(file,algorithm,cores,heuristic,sort,expected). `scripts/run_all.py
--check` runs it; `scripts/run_all.py <folder>` prints the code of every
file × rm/dm/edf and a count per sub-folder (for the report). Both also run
in pytest (`test_custom.py`); the sample check only tests consistency
(EDF schedules whatever RM/DM schedule) and is skipped if the samples are
not found.

### Gantt chart (bonus)

`--plot FILE` saves one PNG per non-empty core (`FILE-coreK.png` with
several cores), drawn from a separate simulation with `simulate(...,
trace=[])`, so the verdict never changes. Cores decided without simulation
are simulated too, only for the chart; unsupported cores get none. Window:
the feasibility interval cut to 200 units, [0, 200) when U > 1 (no busy
period). Bars per execution stretch, triangles at releases, red cross at the
first miss. matplotlib is imported only with `--plot`.

### Choices beyond the statement

- Invalid input (missing file, malformed line, non-positive WCET or period,
  negative offset) → exit **5**, because argparse's default 2 would clash
  with "unsupported".
- The task model is classified **per core**, after partitioning.
- RM/DM on asynchronous arbitrary sets → exit 2 (to confirm with the TA).

## 4. Milestones

- [x] M0 — Plan, repo, notes, session workflow (2026-11-11)
- [x] M1 — Scaffold: package, parsing, model and classification, exit codes,
      CLI skeleton, venv (Windows, Anaconda Python 3.13), VS Code config
      (2026-11-16)
- [x] M2 — `analysis.py` + tests against the guide's examples (2026-11-20)
- [x] M3 — RM/DM/EDF priority functions, feasibility table, unsupported
      messages (2026-11-20)
- [x] M4 — Simulator + `schedulability.py` (uniprocessor complete)
      (2026-11-20)
- [x] M5 — Partitioner + multiprocessor flow (2026-11-23)
- [x] M6 — Custom task sets, `expected.csv`, `run_all.py` over the 60 samples
      (2026-11-23)
- [x] M7 — Bonus visualisation (`--plot`, extra flag) (2026-11-26)
- [ ] M8 — Report (LaTeX) + `package.py` zip, final check against the
      statement

Target: M1–M4 by 20 Nov, M5–M6 by 27 Nov, M7–M8 by 5 Dec (3 days of margin).

## 5. Open questions

- TA: is exit 2 expected for RM/DM on `asynchronous/arbitrary` samples?
