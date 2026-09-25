I'm going to supply a path to you. It will point to either a plan in `docs/plans` or a
ticket in `docs/tickets`. Let's call this path `doc` for now. Please break `doc` down
into beads by doing the following tasks, making sure to replace `doc` with the path I
provide to you.

1. Run `bd prime` if you haven't already this session.
2. Read `doc`. Then read the READMEs and source files for the parts of the codebase that
   `doc` touches.
3. Check whether beads already exist for `doc`: `bd search doc`. If they do, stop and
   tell me instead of creating duplicates.
4. Draft a breakdown and show it to me before creating anything. The breakdown should
   have:
   - One epic for `doc`. A small ticket may be a single task with no epic.
   - Child beads, each small enough to finish in one session and land as one reviewable
     commit. Prefer vertical slices (model, view, template, and tests together) over
     horizontal layers.
   - For each bead: a title, a description, acceptance criteria, and its blockers.
   - Descriptions that let an agent with no prior context start work: which files to
     touch, the approach, and any decisions already made in `doc`.
   - Acceptance criteria that name the tests to write first and require updated docs
     (READMEs, `docs/`) for any files the bead adds, removes, or changes.
   - Questions about anything in `doc` that is ambiguous. Don't guess.
5. Revise the breakdown until I approve it.
6. Create the beads:
   - Epic: `bd create --type epic --title "..." --spec-id doc --description "..."`.
   - Children: `bd create --parent <epic-id> --spec-id doc --title "..."
     --description "..." --acceptance "..."`. Use `--type` (`task`, `feature`, `bug`,
     `chore`) and `--priority` where they differ from the defaults.
   - Blockers: `bd dep add <blocked-id> <blocker-id>`.
7. Verify the result: `bd dep cycles` finds no cycles, and `bd ready --parent <epic-id>`
   lists only the beads that should be startable first.
8. Run `bd export -o .beads/issues.jsonl`, then summarize the epic ID, the bead tree,
   and the beads that are ready to start.
