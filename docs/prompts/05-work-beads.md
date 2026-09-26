I'm going to supply a bead ID to you. Let's call this ID `root` for now. It will be
either an epic with child beads or a single bead with no children. Please do the
following tasks, making sure to replace `root` with the ID I provide to you. You have my
permission to create a branch and make local commits. Do not `git push`, and do not run
`bd dolt push`.

1. Run `bd prime` if you haven't already this session. Then run `bd show root` and read
   the plan or ticket it links to. Note whether `root` has child beads.
2. If you're on `main`, create and switch to a branch named `<root>-<short-slug>`.
3. Work the beads:
   - If `root` has child beads, repeat the steps below until
     `bd ready --parent root` lists nothing, picking the highest-priority bead from
     that list each time.
   - If `root` has no child beads, do the steps below once, with `root` as the bead.

   The steps for each bead are:
   1. Claim the bead with `bd update <id> --claim` and read it with `bd show <id>`.
   2. Write the tests named in the acceptance criteria first and confirm they fail.
   3. Implement until the tests pass.
   4. Update any READMEs and `docs/` files affected by your changes. Scaffold READMEs
      for new files with `uv run docs.py generate --directory <dir>`.
   5. Run `just ci`. Fix anything that fails.
   6. If you find work outside this bead's scope, file it instead of doing it:
      `bd create --deps discovered-from:<id> --title "..." --description "..."`. If
      `root` has child beads, add `--parent root`. Add blockers with `bd dep add` if
      needed.
   7. Close the bead: `bd close <id> --reason "..."`. Then run
      `bd export -o .beads/issues.jsonl`.
   8. Commit the code, docs, and `.beads/issues.jsonl` together. Follow the commit
      message style in `AGENTS.md`.
4. Stop early and tell me if a bead is ambiguous, contradicts the plan or ticket, or
   can't pass `just ci` after a reasonable effort. Leave that bead open with a note
   (`bd update <id> --notes "..."`) explaining where you got stuck.
5. If `root` has child beads, run `bd show root` when nothing is ready. If every child
   bead is closed, close `root` and commit the export.
6. Summarize what you did: the beads you closed, the beads you filed, the beads still
   open or blocked, and your commits.
