---
name: close
description: End a work session on the INFO-F404 scheduler project. Runs the tests, rewrites the status snapshot, appends the journal entry, updates the plan checkboxes and commits, leaving the push to the user. Use when the user says "close" or ends a session.
---

# close — end a session

Run from the repo root (`rt-scheduler/`).

1. **Tests.** `.venv/bin/python -m pytest -q` (if there are tests). Record
   the result as it is; if tests fail, say so and note it as a blocker, do
   not hide it.
2. **`notes/status.md`** — rewrite it as a snapshot, keeping its layout:
   date, current milestone, last commit (fill in after step 6), remote,
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
6. **Commit.** Stage the session's changes (never `.venv`, caches, build
   output or `*.zip`). One commit per logical change when they are
   clearly separate, otherwise one commit. Message: imperative title, a
   few bullets, no `Co-Authored-By` or other AI attribution line. Then put the short hash in `status.md` → "Last commit" and
   amend that change in (or commit it as `notes: update status`).
7. **Hand over the push.** Do not push. Tell the user to run `git push`
   (in the Claude prompt: `! git push`).
8. If a decision is worth keeping in the Obsidian wiki, suggest `/save`
   from a session at the vault root (wiki operations do not run from here).
