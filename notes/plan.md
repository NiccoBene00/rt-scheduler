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
│                            test_simulator, test_partitioner, test_cli
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
decreasing priority order. Theory: guide Cor. 32, Th. 39–40, 44–45, 54, 58,
61–63.

### Decision order (`schedulability.py`)

1. Unsupported combination → 2.
2. Some C_i > D_i, or U > 1 → 3.
3. An exact or sufficient test applies → 0 (or 3 when the test is exact).
4. Otherwise simulate → 0 or 4.

### Simulator

Event-driven: jump to the next release, completion or deadline instead of
stepping one unit at a time (some samples have P ≈ 1.1 M). Jobs released in
the interval are followed until they complete, so a deadline after the end
of the interval is still checked. Stops at the first miss.

### Partitioner

Capacity 1 per core (the statement). BF = eligible core with the highest
load, WF = lowest load, ties to the lowest core index. NF never returns to
earlier cores. Cores are then checked in order; the run stops at the first
core that is not schedulable.

### Choices beyond the statement

- Invalid input (missing file, malformed line, non-positive WCET or period,
  negative offset) → exit **5**, because argparse's default 2 would clash
  with "unsupported".
- The task model is classified **per core**, after partitioning.
- RM/DM on asynchronous arbitrary sets → exit 2 (to confirm with the TA).

## 4. Milestones

- [x] M0 — Plan, repo, notes, session workflow (2026-11-11)
- [ ] M1 — Scaffold: package, parsing, model and classification, exit codes,
      CLI skeleton, venv, VS Code config
- [ ] M2 — `analysis.py` + tests against the guide's examples
- [ ] M3 — RM/DM/EDF priority functions, feasibility table, unsupported
      messages
- [ ] M4 — Simulator + `schedulability.py` (uniprocessor complete)
- [ ] M5 — Partitioner + multiprocessor flow
- [ ] M6 — Custom task sets, `expected.csv`, `run_all.py` over the 60 samples
- [ ] M7 — Bonus visualisation (`--plot`, extra flag)
- [ ] M8 — Report (LaTeX) + `package.py` zip, final check against the
      statement

Target: M1–M4 by 20 Nov, M5–M6 by 27 Nov, M7–M8 by 5 Dec (3 days of margin).

## 5. Open questions

- TA: is exit 2 expected for RM/DM on `asynchronous/arbitrary` samples?
