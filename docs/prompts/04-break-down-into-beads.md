I'm going to describe some work to you. It might be a GitHub issue, my notes, or a plan
we approved in plan mode. Let's call it `work` for now. Please break `work` down into
beads by doing the following tasks.

1. Run `bd prime` if you haven't already this session.
2. Read `work`. Then read the READMEs and source files for the parts of the codebase that
   `work` touches.
3. Check whether beads already exist for `work`: search with `bd search` and
   `bd list --all` for related titles and GitHub issue numbers. If they do, stop and
   tell me instead of creating duplicates.
4. Draft a breakdown and show it to me before creating anything. The breakdown should
   have:
   - One epic for `work`. Small work may be a single task with no epic.
   - For an epic, a design: the problem, the decisions already made and why, and
     anything its children share. This goes in the epic's `--design` field.
   - Child beads, each small enough to finish in one session and land as one reviewable
     commit. Prefer vertical slices (model, view, template, and tests together) over
     horizontal layers.
   - For each bead: a title, a description, acceptance criteria, and its blockers.
   - Descriptions that let an agent with no prior context start work: which files to
     touch, the approach, and any decisions that apply. Beads are the only record, so
     don't point to anything outside them except code and GitHub issues.
   - Acceptance criteria that name the tests to write first and require updated READMEs
     and `docs/` files for any files the bead adds, removes, or changes.
   - Questions about anything in `work` that is ambiguous. Don't guess. If a question
     can't be answered now, make it a `decision` bead labeled `needs-input` that blocks
     the beads waiting on it.
5. Revise the breakdown until I approve it.
6. Create the beads:
   - Epic: `bd create --type epic --title "..." --description "..." --design "..."`.
   - Children: `bd create --parent <epic-id> --title "..." --description "..."
     --acceptance "..."`. Use `--type` (`task`, `feature`, `bug`, `chore`,
     `decision`) and `--priority` where they differ from the defaults.
   - Blockers: `bd dep add <blocked-id> <blocker-id>`.
7. Verify the result: `bd dep cycles` finds no cycles, and `bd ready --parent <epic-id>`
   lists only the beads that should be startable first.
8. Run `bd export -o .beads/issues.jsonl`, then summarize the epic ID, the bead tree,
   and the beads that are ready to start.
