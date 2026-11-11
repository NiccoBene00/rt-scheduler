# Status — snapshot

Rewritten (not appended) at every `close`. History is in `journal.md`.

- **Updated:** 2026-11-11
- **Current milestone:** M1 — Scaffold (not started)
- **Last commit:** see `git log -1` (first commit: setup)
- **Remote:** `origin` = https://github.com/NiccoBene00/rt-scheduler (private), branch `main`
- **Tests:** none yet

## Done

- M0: plan approved (`plan.md`), repo folder, notes, `sync`/`close`
  session commands.

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

1. M1: create `.venv`, `requirements.txt`, the `rtsched` package skeleton,
   `taskset_io.py`, `model.py` (with classification), `exit_codes.py`, the
   CLI skeleton and the `project` launcher, `.vscode/` configs, and
   `tests/test_parsing.py`.

## Open questions / blockers

- TA: exit 2 for RM/DM on asynchronous arbitrary sets?
