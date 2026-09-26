# Remove Continuous Deployment

## The Problem

`.github/workflows/cd.yml` deploys automatically. When the CI workflow succeeds for a
pull request, it deploys the PR's branch to the test server. When CI succeeds for a push
to `main`, it deploys `main` to production. Merging a PR or pushing to `main` therefore
has the side effect of changing a live server. The project has one maintainer, who
already deploys from the command line with `just sted` and `just sprd`, and who would
rather deploy only on purpose.

CD also keeps SSH private keys for both servers in GitHub secrets
(`TEST_SERVER_ANSIBLE_SSH_PRIVATE_KEY` and `PROD_SERVER_ANSIBLE_SSH_PRIVATE_KEY`).
Anyone who can change a workflow on a branch that runs with those secrets can reach the
servers.

## The Technical Plan

Delete `cd.yml` and deploy only with the `just` recipes, which run
`infra/ansible/playbooks/deploy.yml` from the maintainer's machine. CD currently
provides a few things for free. Replace the ones worth keeping:

- **CI gate.** CD only deploys after CI passes. The deploy recipes check that the latest
  CI run for the commit being deployed succeeded, using `gh`, and stop if it didn't.
- **Playbooks match the deployed code.** CD runs the playbook from the commit it
  deploys. A local deploy runs the local playbook while the server pulls the branch from
  GitHub, so an uncommitted or unpushed playbook change can be deployed alongside code
  that doesn't match it. The deploy recipes refuse to run if the working tree is dirty
  or if the local commit differs from the remote branch the server will pull.
- **Deploy history.** The Actions history records what was deployed and when. The
  deploy playbook appends a line to a log file on the server at the end of each
  successful deploy. `src/version.txt` still records the current SHA.

The GitHub deploy secrets are deleted afterward. The CI workflow's own secrets
(`SENTRY_DSN`, `CODECOV_TOKEN`) stay.

Decisions:

- **Fully manual, not `workflow_dispatch`.** A "Run workflow" button would keep the CI
  gate and the Actions logs without deploying on push, but the SSH keys would stay in
  GitHub, and deploys would happen from a browser instead of the terminal.
- **Deploys require `gh`.** The CI check uses the GitHub CLI, so it must be installed
  and logged in (`gh auth login`). `docs/how-to.md` and the README's setup steps say so.
- **The escape hatch is running `ansible-playbook` directly.** The guard checks live in
  the `just` recipes, not the playbook. In an emergency, the maintainer can run the
  playbook command from the recipe by hand to skip them.

## Alternatives

**Keep CD for the test server only.** This keeps the convenience of automatic test
deploys, but merging still changes a server, and the test SSH key stays in GitHub.

**Put the checks in the playbook.** This would guard every way of running it, but the
checks are about the maintainer's local checkout, which Ansible sees only through
`delegate_to: localhost` tasks. A small script called from the recipes is simpler.

## Open Questions

1. Should `just sted` accept an optional branch (e.g., `just sted my-branch`) to keep
   the ability to deploy a PR branch to the test server? CD does this today. The
   inventory sets `repo_branch=main`, so the recipe would pass
   `-e repo_branch=<branch>`. Recommendation: yes, since it's the main thing test
   deploys are for. Production always deploys `main`. **Answer (2026-09-25): Yes.**

## Detailed Implementation

### Step 1 — Guard checks for the deploy recipes

#### `infra/scripts/check-deploy.sh` — create

A Bash script that takes a branch name and exits non-zero with a clear message if:

- `git status --porcelain` shows uncommitted changes.
- After `git fetch origin <branch>`, `git rev-parse HEAD` differs from
  `git rev-parse origin/<branch>`.
- The latest `ci.yml` run for that SHA
  (`gh run list --workflow ci.yml --commit <sha> -L1 --json conclusion,status`) is
  missing, still running, or not `success`.

#### `justfile` — modify

`server-test-deploy` and `server-prod-deploy` run the script before the playbook.
`server-prod-deploy` checks `main`. `server-test-deploy` takes an optional `branch`
argument (default `main`), checks that branch, and passes `-e repo_branch={{ branch }}`.

#### Tests

There is no shell test setup. Check the script by hand: it fails with a dirty tree,
fails when the local commit isn't pushed, fails for a commit whose CI failed, and passes
on a pushed, green `main`. Run `shellcheck` on it if it's available.

### Step 2 — Server-side deploy log

#### `infra/ansible/tasks/admin/deploy_log.yml` — create

An `ansible.builtin.lineinfile` task (`create: true`, `insertafter: EOF`) that appends
`<UTC timestamp> <short SHA> <branch>` to `{{ repo_dir }}/../deploys.log`. The file is
outside the repo, so `git pull` never touches it.

#### `infra/ansible/playbooks/deploy.yml` — modify

Include `deploy_log.yml` as the last task, after the Gunicorn restart, so only
successful deploys are logged.

When `docs/plans/004-backup-and-restore.md` Step 3 lands, it should add the
pre-deployment backup name to this line.

### Step 3 — Remove CD and update the docs

#### `.github/workflows/cd.yml` — delete

#### `README.md` — modify

Remove the continuous deployment badge.

#### `docs/how-to.md` — modify

Rewrite "How to Manually Deploy the HCI" as "How to Deploy the HCI". Deploys are only
manual. Explain the guard checks, the optional test branch, where the deploy log lives,
and the escape hatch.

#### `docs/plans/004-backup-and-restore.md` — modify

It assumes CD in three places: the problem statement ("every push to `main` runs
`.github/workflows/cd.yml`"), Step 3 ("so it shows up in the GitHub Actions deploy
log"), and the revert runbook ("Find the bad deploy's backup name in its GitHub Actions
deploy log" and "The next CD deploy will..."). Change these to the terminal output, the
server's deploy log, and a manual `just sprd`. Update beads `hci-l0k.8` and `hci-l0k.11`
to match.

#### Manual step for the maintainer

Delete these GitHub secrets: `TEST_SERVER_ANSIBLE_SSH_PRIVATE_KEY`, `TEST_SERVER_IP`,
`TEST_SERVER_ANSIBLE_USER`, `TEST_SERVER_REPO_DIR`,
`PROD_SERVER_ANSIBLE_SSH_PRIVATE_KEY`, `PROD_SERVER_IP`, `PROD_SERVER_ANSIBLE_USER`,
and `PROD_SERVER_REPO_DIR`. Consider rotating the two SSH keys, since they have been
stored in GitHub.
