---
name: sync
description: Start a work session on the INFO-F404 scheduler project. Pulls the latest code, reads the notes and reports where we left off and the next step. Use when the user says "sync" or starts a session.
---

# sync — open a session

Run from the repo root (`rt-scheduler/`).

1. **Local state.** `git status --short` and `git branch --show-current`.
   If there are uncommitted changes, list them and ask before pulling.
2. **Pull.** If `origin` exists: `git pull --ff-only`. If it fails
   (diverged or no network), stop and report; never force or rebase on your
   own.
3. **Read the notes**, in this order:
   - `notes/status.md` (the snapshot: milestone, last commit, next step),
   - the last entry of `notes/journal.md`,
   - in `notes/plan.md`, the section for the current milestone and any
     design point it needs.
4. **What changed since the last close.** Compare the last commit in
   `status.md` with `HEAD`: `git log --oneline <last>..HEAD`. If there are
   commits made outside a session (e.g. the user coded by hand), read
   `git diff <last>..HEAD` and summarise them.
5. **Health check.** If `.venv/` exists and `tests/` has tests:
   `.venv/bin/python -m pytest -q`. If `.venv/` is missing (fresh clone),
   say so and offer:
   `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
6. **Report** in a few lines:
   - pull result and new commits, if any,
   - current milestone and what is done,
   - test result,
   - days left until 8 December 2026,
   - the next step from `status.md`, as a proposed goal for this session.

   Then wait for the user to confirm or change the goal.

Do not edit any file during `sync`.
