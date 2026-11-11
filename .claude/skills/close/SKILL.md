---
name: close
description: End a work session on the INFO-F404 scheduler project. Runs the tests, rewrites the status snapshot, appends the journal entry, updates the plan checkboxes, then gives the user the git commands to commit and push from VS Code. Use when the user says "close" or ends a session.
---

# close — end a session

Run from the repo root (`rt-scheduler/`).

1. **Tests.** `.venv/Scripts/python.exe -m pytest -q` (if there are tests). Record
   the result as it is; if tests fail, say so and note it as a blocker, do
   not hide it.
2. **`notes/status.md`** — rewrite it as a snapshot, keeping its layout:
   date, current milestone, remote,
   test result, done list, the module table, **next step** (concrete enough
   that a new session can start without this conversation), open questions.
3. **`notes/journal.md`** — append one entry at the bottom:
   `## YYYY-MM-DD — Session N: <topic>` with **Done**, **Decisions** (each
   with its reason), **Problems** (if any) and **Next**. Facts only; never
   rewrite earlier entries.
4. **`notes/plan.md`** — tick finished milestones. If a design decision
   changed this session, update the design section (the reason goes in
   the journal).
5. **Show** `git status --short` and a short summary of the diff.
6. **Give the git commands, do not run them.** Claude never runs
   `git add`, `git commit` or `git push`. Write, ready to paste in the VS
   Code terminal (PowerShell):
   - `git add <paths>` for the session's work (never `.venv`, caches,
     build output or `*.zip`), with one commit per logical change when
     clearly separate;
   - `git commit -m "<title>" -m "<bullets>"`: imperative title, a few
     bullets, no `Co-Authored-By` or other AI attribution line;
   - the notes in a last commit: `git add notes/` and
     `git commit -m "notes: close session N"` (`sync` finds the previous
     session by this message);
   - `git push`.
7. After the user pastes the result, check with `git status -sb` and
   `git log --oneline -3` that everything is committed and pushed.
8. If a decision is worth keeping in the Obsidian wiki, suggest `/save`
   from a session at the vault root (wiki operations do not run from here).
