# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:46cd31e7 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

## Build & Test

We use `just` for common tasks. Run `just --list` to see every recipe.

```bash
just test-all          # Run all tests (uv run pytest -n auto)
just ci                # Run formatters, linters, type checks, Django checks, and tests
just django-runserver  # Run the development server
just django-migrate    # Apply migrations
```

## Architecture Overview

This project is a simple Django web application that provides a way for genetics
experts to curate information about HLA alleles and haplotypes and their relationships
to diseases.

In docs.json, we list important directories that have READMEs. Each README has a brief
overview of the directory followed by short descriptions of each non-ignored file in the
directory.

## Conventions & Patterns

- We strive for high test coverage, and when reasonable, we follow test-driven
  development.
- We use Google docstrings.
- We use American English.
- When writing Markdown, the text width is 88 characters.

## Keeping Documentation Up-to-Date

Documentation changes are part of every code change, not a follow-up task. When you add,
remove, rename, or significantly change a file, update the README in its directory in
the same change. If you add a directory that belongs in docs.json, add it there and
scaffold its README with `uv run docs.py generate --directory <dir>`. If a change makes
anything in `docs/` inaccurate, update that too.

## Our Beads Workflow

1. Large work is described in a plan in `docs/plans`. Small work is described in a
   ticket in `docs/tickets`. Both use the naming scheme `NNN-short-name.md`. If you
   write a plan in plan mode, save the approved plan to `docs/plans`.
2. `docs/prompts/04-break-down-into-beads.md` turns a plan or ticket into an epic with
   child beads. Each bead links back to its plan or ticket with `--spec-id`.
3. `docs/prompts/05-work-beads.md` works through a single bead, or through an epic's
   beads until none are ready.

Beads and tickets don't correspond one-to-one. A ticket or plan can produce one bead or
many, and small, self-contained work can be a bead with no ticket at all. Write a ticket
when the work needs more context than fits in a bead: a decision to record, an open
question, or reasoning someone might question later. Otherwise, create the bead
directly with a description that lists the files to change and acceptance criteria
that name the tests to write.

When working on a bead, follow its acceptance criteria and read the plan or ticket it
links to, if it has one. File work you discover outside a bead's scope as a new bead
instead of doing it. After changing beads, run `bd export -o .beads/issues.jsonl` so
the export in git stays current. Don't commit, push, or run `bd dolt push` unless a
prompt or I tell you to.
