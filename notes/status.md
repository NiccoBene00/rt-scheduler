# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-11 (close of session 1)
- **Current milestone:** M1 — Scaffold (environment done, no code yet)
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** none yet

## Done

- M0: plan approved (`plan.md`), notes, `sync`/`close` session commands,
  GitHub repo (pushed).
- M1, environment part: Windows `.venv` (Anaconda Python 3.13.5, pytest
  9.2.0, matplotlib 3.11.2), `requirements.txt`, `.vscode/settings.json`
  (venv interpreter, pytest, LF) and `.vscode/launch.json` ("rtsched: run
  on a task set" asks for file, algorithm and cores; "Python: current
  file").

## Code state

No code yet.

| Module | State |
|---|---|
| taskset_io, model | — |
| analysis | — |
| schedulers (rm, dm, edf) | — |
| feasibility, schedulability | — |
| simulator | — |
| partitioner | — |
| cli, exit codes | — |
| visualization (bonus) | — |
| report | — |

## Next step

M1, code part. Write one file at a time in the chat, and the user types it:

1. `rtsched/__init__.py`, `rtsched/__main__.py`, `rtsched/exit_codes.py`
   (0–4 from the statement, plus 5 = invalid input).
2. `rtsched/model.py`: `Task`, `TaskSet`, `Job` and classification
   (sync/async, implicit/constrained/arbitrary).
3. `rtsched/taskset_io.py`: parse `offset;wcet;deadline;period`, with
   validation → exit 5.
4. `rtsched/cli.py` skeleton (argparse with the statement's flags and
   defaults) and the `project` launcher.
5. `tests/test_parsing.py`, then check the "rtsched: run on a task set"
   launch config with F5.

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
- Network: GitHub's EU servers (140.82.121.x) are sometimes unreachable
  from the home network; if a push hangs, push from another network or
  retry later.
