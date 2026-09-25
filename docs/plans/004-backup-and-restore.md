# Database Backup and Restore

## The Problem

The HCI stores everything curators produce in a single SQLite file. `DATABASES` in
`src/config/settings/base.py` points at `BASE_DIR / "hci.db"`, which on the production
server is `/home/ubuntu/hla-curation-interface/src/hci.db` (the Ansible inventory sets
`repo_dir` to `/home/ubuntu/hla-curation-interface`). The file lives on the local disk
of a single AWS Lightsail instance (`infra/terraform/server.tf`), and there are no
backups of it today:

- Nothing in `pyproject.toml` provides backups (no django-dbbackup, no S3 client).
- No Ansible task, cron job, or systemd timer copies the database anywhere.
- The Lightsail instance in `server.tf` has no `add_on` block, so Lightsail automatic
  snapshots are off. Manual snapshots may have been taken in the console, but nothing
  in the repo does it.
- There are no uploaded files (no `FileField` or `ImageField` in any model), so the
  database is the only data we need to protect.

Two things can go wrong. First, a deploy can break things: every push to `main` runs
`.github/workflows/cd.yml`, which runs `infra/ansible/playbooks/deploy.yml`, which runs
`manage.py migrate` against the live database. A bad migration or a bug in new code can
damage data, and there is no way back to the state before the deploy. Second, the
instance can be lost, or a bug can quietly corrupt data over days. In either case,
curation work is gone for good.

The goal is:

1. A backup of the database taken automatically before every deploy, so a bad deploy
   can be reverted (both code and data) to exactly where it was.
2. A daily backup, so there is a recent restore point even when damage is found long
   after a deploy.
3. Backups stored off the server, in S3.
4. A regular, automated check that the backups can actually be restored.
5. A written, rehearsed procedure (and an Ansible playbook) for reverting a bad deploy
   and for restoring from a backup.

## The Technical Plan

**Tool.** We use [django-dbbackup](https://github.com/Archmonger/django-dbbackup) with
S3 storage via django-storages. For SQLite, django-dbbackup 5.x uses
`SqliteBackupConnector` by default, which uses SQLite's online backup API. This takes a
consistent copy even while Gunicorn is serving requests, which a plain `cp` does not
promise. Restoring writes the backup file over `hci.db`, so the app must be stopped
while restoring. Backups are gzip-compressed (`--compress`).

**Storage.** Terraform creates one private S3 bucket per workspace (test and prod), with
public access blocked, default server-side encryption, and a lifecycle rule that deletes
objects older than 90 days. No versioning is needed, because every backup has a unique
name. Backups go under three key prefixes, so the right one is easy to find during an
incident:

- `pre-deployment/`: taken by the deploy playbook before `migrate`.
- `daily/`: taken by a daily timer on the server.
- `pre-restore/`: taken by the restore playbook just before it overwrites the database,
  so a restore can itself be undone.

Lightsail instances can't have IAM instance roles, so the server uses an IAM user whose
policy allows only list, get, put, and delete on its own bucket. Its keys go in the
server's `.env`. A second, read-only IAM user for the prod bucket is used by the weekly
restore-check workflow in GitHub Actions.

**Pre-deployment backup.** The deploy playbook currently runs: apt update, apt upgrade,
git pull, write the git SHA to `src/version.txt`, uv sync, npm ci, migrate,
collectstatic, restart Gunicorn. We add two things. Before `git pull`, the playbook
reads the SHA of the code that is running now from `src/version.txt`. After `npm ci` and
before `migrate`, it runs `dbbackup`, so the new code's dependencies (including
django-dbbackup itself on the first deploy) are installed. The backup is named after
both SHAs, for example
`pre-deployment/hci-3f2a9c1-to-88c5e47-2026-09-25T180102Z.sqlite3.gz`. This backup holds
the data exactly as the old code left it. The "from" SHA says which code matches it,
which is what a revert needs. If the backup fails, the play stops before `migrate`.
Ansible `command` tasks already fail on a non-zero exit, and we must not add
`ignore_errors`.

**Daily backup.** A systemd timer on the server runs a small management command,
`backup_db`, once a day at a low-traffic time. The command wraps `dbbackup` and reports
a check-in to Sentry Crons, so a missed or failed backup sends an alert through the
Sentry account we already use (see "Error Monitoring and Uptime" in `docs/design.md`).
We use a systemd timer instead of cron so the output goes to journald with the rest of
the app's logs (see `docs/plans/006-logging.md`). The timer is installed by Ansible.
Because `init.yml` can't safely be re-run on a live server (it runs `loaddata` and
`caddy start`), the timer files are placed from `deploy.yml`. Placing the files and
enabling the timer can be re-run safely.

**Weekly restore check.** A scheduled GitHub Actions workflow runs once a week. It
checks out `main` (the code prod runs), installs dependencies, restores the newest
`daily/` backup from S3 into a new database on the runner, runs `migrate --check` and
`check`, starts Gunicorn, and requests `/repo/download/all.json`, checking for a 200 and
a non-empty JSON list. GitHub emails the repo owner when a scheduled workflow fails.
Running on the runner, not on the test server, fixes a problem the first draft of this
plan pointed out. The test server runs whatever branch was deployed last, so
`migrate --check` there fails when test has migrations prod doesn't. That mixes up
"the backup is bad" with "the schemas are out of sync." Checking against `main` tests
only the backup. It also keeps prod data (user emails and curation data covered by the
PHI agreement) off the test server.

**Revert and restore.** A new playbook, `infra/ansible/playbooks/restore.yml`, handles
two cases with one procedure:

- **Revert a bad deploy.** Restore the `pre-deployment/` backup for that deploy, and
  check out its "from" SHA. Code and data go back together to the state before the
  deploy.
- **Recover from data corruption.** Restore a `daily/` (or `pre-deployment/`) backup and
  keep the current code, or check out a given SHA.

The playbook stops `gunicorn.socket` and `gunicorn.service`. Both must stop, because the
socket unit would start the service again on the next request. It then takes a
`pre-restore/` backup, checks out the requested SHA if one was given, runs uv sync and
npm ci, writes `src/version.txt`, runs `dbrestore --noinput`, runs `migrate` (a no-op
when code and backup match), runs collectstatic, and starts both units again. Just
recipes wrap it for test and prod. A runbook in `docs/how-to.md` says when to use which
backup, and says that after reverting prod you must push a `git revert` of the bad
commit to `main`. If you don't, the next deploy puts the bad code back.

## Alternatives

**Lightsail automatic snapshots only.** Lightsail can take a daily snapshot of the whole
instance (an `add_on { type = "AutoSnapshot" }` block on `aws_lightsail_instance`). It
costs little and covers the whole machine, including `.env` and Caddy's certificates.
But you can't take one on demand before each deploy from Ansible without extra AWS
tooling, you can't restore just the database without building a new instance, and
snapshots are kept only 7 days. It works well alongside this plan, not in place of it.
See Open Question 3.

**Plain `sqlite3 .backup` plus `aws s3 cp`.** A shell script run by the timer could do
the same work with no new Python dependencies. django-dbbackup gives us naming,
compression, restore, and listing backups (`listbackups`) as management commands that
fit the rest of the project. It would also keep working if we ever move off SQLite.

**Litestream.** Litestream streams SQLite changes to S3 all the time, so you can restore
to any point in time. That is more than a low-traffic curation tool needs, and it adds
a daemon to run and watch. It is worth another look if losing up to a day of work
between daily backups is too much.

**Reverse migrations instead of restoring.** A bad deploy could be undone with
`migrate <app> <previous_migration>` and a code rollback. That keeps data entered after
the deploy, but it only works when every migration can be reversed and the bug didn't
damage data. Restoring the pre-deployment backup always works, but it loses anything
entered after the deploy. The runbook should say that reverse migrations are an option
when the damage is only to the schema.

**`git revert` on `main` as the only code rollback.** The first draft of this plan
restored the database first and then pushed a `git revert`, leaving CD to deploy the
old code. That means the site runs new code on the old schema for as long as CI and CD
take, and the revert has to pass CI during an incident. The restore playbook changes
code and data together while the app is stopped. The `git revert` still has to happen
afterward, but nothing waits on it.

**Restore check on the test server.** The first draft restored prod's backup onto the
test server over SSH each week. It also tests the real server setup, but it has the
schema drift and prod-data problems described above.

## Open Questions

1. **Is a restore that loses data entered since the deploy acceptable?** Restoring a
   pre-deployment backup drops every change made after the deploy. The plan assumes
   that's fine for this tool: traffic is low, and `pre-restore/` backups keep the lost
   data if someone needs to copy it back by hand. This blocks the runbook wording
   (Step 6).
2. **Should backups be encrypted client-side?** The bucket uses S3 server-side
   encryption, and only the two IAM users can read it. The database holds user emails
   and data covered by the PHI agreement (`docs/design.md`). django-dbbackup can also
   GPG-encrypt backups (`--encrypt`), but then a GPG key has to be kept safe and made
   available on the server and in GitHub Actions. This blocks Step 2 and Step 3.
3. **Should we also turn on Lightsail automatic snapshots?** It's cheap protection for
   the whole server (including `.env`). This doesn't block anything else. It's one
   Terraform block (Step 1).
4. **Is Sentry Crons available on our Sentry plan?** The daily backup alert depends on
   it. If not, the fallback is an UptimeRobot heartbeat monitor (UptimeRobot is already
   used, per `docs/design.md`), or relying on the weekly restore check to notice missing
   backups. This blocks Step 4.
5. **Should test deploys take pre-deployment backups?** The plan says yes, so the backup
   step runs on every PR deploy before it runs on prod, and the test bucket's lifecycle
   rule cleans up. The cost is one S3 upload per PR deploy. This blocks Step 3.
6. **Backup time and retention.** The plan uses 09:00 UTC (1–2 AM Pacific) for the daily
   backup and keeps backups 90 days. Confirm, or pick other values. This doesn't block
   anything (the defaults can go in as proposed).

## Detailed Implementation

The work comes in the order it can be deployed. Each step leaves prod working. Ansible
changes follow the current layout: install tasks in `tasks/install/`, file placement in
`tasks/placement/`, and service or admin actions in `tasks/admin/`. `infra/` has no
READMEs, and `docs.json` doesn't list it, so infra changes are documented in
`docs/how-to.md`.

### Step 1 — S3 bucket and IAM users

#### `infra/terraform/backup.tf` — create

Define, per workspace:

- `aws_s3_bucket.backups` named `hci-backups-${terraform.workspace}` on the
  `aws.stanford-clingen-projects` provider.
- `aws_s3_bucket_public_access_block` with all four settings `true`.
- `aws_s3_bucket_server_side_encryption_configuration` with `AES256`.
- `aws_s3_bucket_lifecycle_configuration` with one rule that expires every object after
  90 days.
- `aws_iam_user.backup_writer` (`hci-backup-writer-${terraform.workspace}`) and an
  inline `aws_iam_user_policy` allowing `s3:ListBucket` on the bucket and
  `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` on `bucket/*`. Add an
  `aws_iam_access_key` for it.
- In the `prod` workspace only (`count = terraform.workspace == "prod" ? 1 : 0`),
  `aws_iam_user.backup_reader` with only `s3:ListBucket` and `s3:GetObject`, plus an
  access key.
- `output`s for the bucket name and access key IDs, and `sensitive = true` outputs for
  the secrets. The secrets end up in the Terraform state, which is kept encrypted in
  the `stanford-infra` bucket (`main.tf`).

Optionally (Open Question 3), add an `add_on { type = "AutoSnapshot" snapshot_time =
"08:00" status = "Enabled" }` block to `aws_lightsail_instance.hci` in
`infra/terraform/server.tf`.

Check with `just terraform-format-check` and `just terraform-lint`, then run
`terraform apply` in the `test` and `prod` workspaces.

#### `docs/how-to.md` — modify

Add a "How to Configure Backup Credentials" section. It covers reading the Terraform
outputs, adding `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and
`DBBACKUP_BUCKET_NAME`, plus `SUBDOMAIN` (`hci` or `hci-test`, used in backup names),
to each server's `.env` (the `.env` is kept by hand, and Ansible doesn't manage it),
and adding the reader keys to GitHub as `BACKUP_READER_AWS_ACCESS_KEY_ID`,
`BACKUP_READER_AWS_SECRET_ACCESS_KEY`, and `PROD_BACKUP_BUCKET_NAME`.

### Step 2 — Install and configure django-dbbackup

#### `pyproject.toml` — modify

Add `django-dbbackup>=5.3` and `django-storages[s3]` to `dependencies`, then run
`uv lock`.

#### `src/config/settings/base.py` — modify

Add `"dbbackup"` to `INSTALLED_APPS`. Add a `"dbbackup"` entry to `STORAGES`:

- If `DBBACKUP_BUCKET_NAME` is set in the environment, use
  `storages.backends.s3.S3Storage` with `bucket_name`, `region_name="us-west-2"`, and
  `default_acl=None`. The keys come from the standard `AWS_*` environment variables.
- Otherwise, use `django.core.files.storage.FileSystemStorage` with `location` set to
  `BASE_DIR.parent / "backups"`, so dev and CI work without AWS.

Set `DBBACKUP_FILENAME_TEMPLATE` so default names (used by the daily backup) look like
`daily/{servername}-{datetime}.{extension}`. Set `DBBACKUP_HOSTNAME` from
`os.getenv("SUBDOMAIN", "dev")`, so names say `hci` or `hci-test` rather than the
Lightsail hostname. Leave the connector at the default `SqliteBackupConnector`. If Open
Question 2 is answered yes, add the `DBBACKUP_GPG_RECIPIENT` settings here.

#### `.gitignore` — modify

Add `backups/`.

#### `src/common/tests.py` — modify

Write these tests first. With `STORAGES["dbbackup"]` overridden to a temporary
`FileSystemStorage` (`override_settings` plus `tmp_path`), `call_command("dbbackup",
"--noinput", "--compress", "-o", "pre-deployment/x.sqlite3.gz")` writes that file, and
`call_command("dbrestore", "--noinput", "--uncompress", "-i", ...)` brings back a row
that was deleted after the backup. This proves the settings work and that a round trip
keeps the data.

#### `src/config/README.md` — modify

Describe the new `dbbackup` storage entry in the `settings/base.py` section. Mention the
root `backups/` directory used in dev in the root `README.md` if it has a setup section.

### Step 3 — Pre-deployment backup in the deploy playbook

#### `infra/ansible/tasks/admin/git_sha_previous.yml` — create

Use `ansible.builtin.slurp` to read `{{ repo_dir }}/src/version.txt` (`failed_when:
false`), and `set_fact` `previous_sha` to its trimmed contents, or to `unknown` if the
file is missing.

#### `infra/ansible/tasks/admin/django_dbbackup_predeploy.yml` — create

`set_fact` `current_sha` from `version.txt` (written by `git_sha.yml`), a UTC
timestamp `ts` from `ansible_date_time`, and `backup_name`. Then run `dbbackup` with
`chdir: {{ repo_dir }}/src`:

```
backup_name: "pre-deployment/{{ subdomain }}-{{ previous_sha }}-to-{{ current_sha }}-{{ ts }}.sqlite3.gz"

~/.local/bin/uv run manage.py dbbackup --noinput --compress -o "{{ backup_name }}"
```

Tag it `skip_ansible_lint`, like the other `command` tasks. Don't use `ignore_errors`,
so a failure stops the play before `migrate`. Print the backup name with `debug`, so it
shows up in the GitHub Actions deploy log. That's where you'll look for it during an
incident.

#### `infra/ansible/playbooks/deploy.yml` — modify

Include `git_sha_previous.yml` before "Git pull". Include
`django_dbbackup_predeploy.yml` after "npm install" and before "Django migrate". Don't
add it to `init.yml`, since there's no database to back up on a fresh server.

The first deploy of this step must come after Step 1's `.env` changes are on both
servers. If they aren't, the backup task fails and stops the deploy, which is what we
want. Deploy to test through a PR, check that the file is in the bucket, then merge.

### Step 4 — Daily backup timer with Sentry Crons

#### `src/common/management/commands/backup_db.py` — create

A `BaseCommand` that calls `call_command("dbbackup", "--noinput", "--compress")` inside
`sentry_sdk.crons.monitor(monitor_slug=f"hci-daily-backup-{hostname}")`, where hostname
is `settings.DBBACKUP_HOSTNAME`, with a `monitor_config` giving the crontab schedule and
a check-in margin. Create the `management/` and `management/commands/` packages with
empty `__init__.py` files. Use a Google-style docstring.

#### `src/common/tests.py` — modify

Test first. `backup_db` writes exactly one file under `daily/` in a temporary
`FileSystemStorage`. Patch `sentry_sdk.crons.monitor` to check that it's entered with
the expected slug. When `dbbackup` raises an error, the error reaches the caller, so
systemd marks the run as failed.

#### `infra/ansible/tasks/placement/files/templates/hci-backup.service` — create

A `Type=oneshot` unit with `User={{ ansible_user }}`, `WorkingDirectory={{ repo_dir
}}/src`, and `ExecStart={{ repo_dir }}/.venv/bin/python manage.py backup_db`.
`manage.py` loads `.env` itself.

#### `infra/ansible/tasks/placement/files/hci-backup.timer` — create

`OnCalendar=*-*-* 09:00:00 UTC`, `Persistent=true` (so a missed run happens at boot),
and `WantedBy=timers.target`.

#### `infra/ansible/tasks/placement/backup_timer.yml` — create

Copy both files to `/etc/systemd/system/`, following `tasks/placement/gunicorn.yml`.

#### `infra/ansible/tasks/admin/backup_timer_start.yml` — create

Use `ansible.builtin.systemd` with `name: hci-backup.timer`, `enabled: true`,
`state: started`, and `daemon_reload: true`.

#### `infra/ansible/playbooks/deploy.yml` and `init.yml` — modify

Include the two tasks at the end of both playbooks. They can be re-run safely, so
existing servers get the timer on their next deploy.

#### `src/common/README.md` — modify

Describe `management/commands/backup_db.py`.

### Step 5 — Weekly restore check

#### `.github/workflows/restore-check.yml` — create

Trigger it with `schedule: cron: "0 10 * * 1"` and `workflow_dispatch`. It's one job:

1. Check out `main`. Use `./.github/actions/install-python-dependencies` and
   `install-javascript-dependencies`, then run `just django-collectstatic`.
2. Set env the same way `ci.yml` does (dummy Clerk keys and `SECRET_KEY`,
   `DJANGO_SETTINGS_MODULE=config.settings.prod`, `SENTRY_ENV=restore-check`), plus the
   reader keys and `DBBACKUP_BUCKET_NAME` from secrets.
3. Run `cd src && uv run manage.py listbackups` to find the newest `daily/` backup.
   Fail if it's older than 48 hours. This also catches a timer that has quietly stopped.
4. Run `uv run manage.py dbrestore --noinput --uncompress -i <name>`.
5. Run `uv run manage.py migrate --check`, then `uv run manage.py check`.
6. Start `.venv/bin/gunicorn config.wsgi:application -b 127.0.0.1:8000` in the
   background. Run `curl -fsS -H "Host: hci.clinicalgenome.org"
   http://127.0.0.1:8000/repo/download/all.json`, and check with `jq` that it's a
   non-empty array.

Check with `just gh-actions-format-check` and `just gh-actions-lint`.

### Step 6 — Restore playbook and runbook

#### `infra/ansible/playbooks/restore.yml` — create

It takes the variables `backup_name` (required) and `restore_sha` (optional). Use an
`assert` at the start to require `backup_name`. The tasks, in order:

1. Stop `gunicorn.socket` and `gunicorn.service` (new
   `tasks/admin/gunicorn_stop.yml`).
2. Take a `pre-restore/{{ subdomain }}-{{ ts }}.sqlite3.gz` backup (new
   `tasks/admin/django_dbbackup_prerestore.yml`, based on the pre-deployment one).
3. If `restore_sha` is set, check it out with `ansible.builtin.git` (`version: "{{
   restore_sha }}"`), then include `git_sha.yml`, `uv_sync.yml`, and `npm_install.yml`.
4. Run `manage.py dbrestore --noinput --uncompress -i {{ backup_name }}` (new
   `tasks/admin/django_dbrestore.yml`).
5. Include `django_migrate.yml` and `django_collectstatic.yml`.
6. Start `gunicorn.socket` and `gunicorn.service` again (`gunicorn_start.yml`).

If any step after step 1 fails, the site stays down. That's safer than serving code
that doesn't match the schema. The runbook explains how to recover by hand.

#### `justfile` — modify

Add `server-test-restore backup sha=""` and `server-prod-restore backup sha=""` in the
Server group. They run `ansible-playbook ... playbooks/restore.yml --limit ... -e
backup_name={{ backup }} -e restore_sha={{ sha }}`. Add a `server-prod-list-backups`
recipe that runs `listbackups` on the server over an Ansible ad hoc `command`.

#### `docs/how-to.md` — modify

Add "How to Revert a Bad Deploy":

1. Find the bad deploy's backup name in its GitHub Actions deploy log, or run
   `just server-prod-list-backups` and look for `pre-deployment/hci-<from>-to-<bad>-*`.
2. Run `just server-prod-restore pre-deployment/hci-<from>-to-<bad>-<ts>.sqlite3.gz
   <from>`.
3. Check the site. Check that the footer's git SHA (from
   `common.context_processors.git_sha`) shows `<from>`.
4. Open a PR with `git revert <bad>` and merge it. The next CD deploy will make a
   pre-deployment backup, run a no-op `migrate`, and move the server back onto `main`.
   Until then, don't merge anything else.
5. If users entered data after the bad deploy that should be kept, it's in the
   `pre-restore/` backup. Copy it back by hand (see Open Question 1).

Add "How to Restore After Data Corruption". Pick the newest `daily/` backup from before
the damage started. Run `just server-prod-restore <backup>` without a SHA if the
current code matches that backup's schema (the playbook's `migrate` brings it up to
date otherwise). Add a note about reverse migrations as an option when only the schema
was damaged. Rehearse both procedures on the test server once they're written.

## Sources

- Notes: "HCI: Work on backup and revert"
- Notes: "HCI: Database backups"
- The first draft of this plan, `docs/plans/004-backup-and-restore-DRAFT.md`
