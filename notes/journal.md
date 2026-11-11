# Journal

One entry per work session, newest at the bottom, appended at `close`.
Each entry: what was done, decisions and why, problems, next step.

## 2026-11-11 — Session 1: plan and setup

**Done**
- Read the statement, the sample task sets, the Practice 1 simulator and
  the wiki pages on feasibility intervals, EDF and partitioning.
- Wrote and approved the plan (`plan.md`): structure, feasibility table,
  decision order, milestones M0–M8.
- Created the repo folder, `notes/`, `CLAUDE.md` and the `sync`/`close`
  session commands. Git configured (identity, Windows credential manager),
  remote `origin` on GitHub (private), first commit.

**Decisions**
- Event-driven simulator: some samples have P ≈ 1.1 M, so stepping one unit
  at a time up to O_max + 2P would be too slow in Python.
- Exit 5 for invalid input, so it can't be confused with exit 2.
- Model classified per core after partitioning.
- No AI attribution line in commits, as in the thesis.
- Dev notes and `.claude/` live in the repo (they travel with git) but are
  left out of the hand-in zip.

**Next**
- M1 (scaffold).
