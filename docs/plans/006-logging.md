# Logging

## The Problem

Production logging grew without a plan. The notes ask three questions: "Right now, I
believe we write logs to a file in production. Do we do anything else? Do we rotate log
files?" Here is what the code does today.

**Django writes to a file and to stderr.** `LOGGING` in `src/config/settings/prod.py`
sends the root logger at `INFO` to two handlers:

- `file`: a `logging.handlers.RotatingFileHandler` writing to `logs/hci.log` in the
  repository root (`BASE_DIR.parent / "logs"`, which is
  `/home/ubuntu/hla-curation-interface/logs/hci.log` on the servers). It uses the
  `verbose` format (level, time, module, pid, thread, logger name, message).
- `console`: a `StreamHandler` writing to stderr with the `simple` format (just level
  and message, with no time or logger name).

`prod.py` also creates the `logs/` directory and touches `hci.log` when the module is
imported. That side effect runs everywhere the prod settings load, including
`manage.py migrate` and `collectstatic` during deploys, and the CI jobs in
`.github/workflows/ci.yml` and `codecov.yml` that set
`DJANGO_SETTINGS_MODULE=config.settings.prod`.

**Yes, the file rotates, but only by size.** The handler keeps `hci.log` plus five
backups of 5 MB each, so at most about 30 MB. Nothing limits it by time. On a quiet week
that could hold months of history. During a burst of errors it could hold only hours. It
isn't safe across processes either. `RotatingFileHandler` assumes one process writes the
file. Gunicorn runs a single worker today (`gunicorn.service` doesn't pass `--workers`),
but deploy-time management commands write to the same file. The daily backup timer from
`docs/plans/004-backup-and-restore.md` will too. Lines written near a rotation can end
up in the wrong file or be lost.

**We also log to journald, without meaning to.** Gunicorn runs as the systemd unit in
`infra/ansible/tasks/placement/files/templates/gunicorn.service`, so its stderr goes to
the systemd journal. Every Django log line is therefore stored twice: once in
`hci.log`, and once in the journal in the shorter `simple` format. Gunicorn's own
messages (worker boots, timeouts, crashes) go only to the journal. Gunicorn's access log
is off (the default), which is fine because Caddy logs every request. We never
configured journald, so it uses Ubuntu 24.04's defaults: persistent storage in
`/var/log/journal`, capped at 10% of the disk (at most 4 GB), with no time limit.

**Caddy writes a JSON access log that it rotates itself.** The Caddyfile template
(`infra/ansible/tasks/placement/files/templates/Caddyfile`) writes access logs as JSON
to `/var/log/caddy/access.log`. fail2ban reads this file (`jail.d/caddy.conf`, from
`docs/plans/002-bot-protection.md`). Caddy's file output rolls by default at 100 MB,
keeps 10 files, and deletes files older than 90 days. We rely on those defaults without
writing them down. Caddy is started with `caddy start` (`tasks/admin/caddy_start.yml`),
not through the `caddy.service` unit the apt package installs. It isn't clear from the
repo where Caddy's own runtime logs (certificate renewals, config errors) end up, or
whether the packaged unit is also running. This needs to be checked on the servers.

**Sentry already alerts on errors.** `src/config/settings/base.py` sets up
`sentry_sdk` with its default Django and logging integrations. Unhandled exceptions,
and log records at `ERROR` and above (for example, `logger.exception` in the
`clients.py` modules and `auth_/views.py`), become Sentry events. `INFO` records are
attached as breadcrumbs. UptimeRobot watches the public URL (`docs/design.md`). Whether
Sentry actually sends email or Slack alerts depends on alert rules in the Sentry
project, and we can't see those from the repo.

**Nothing leaves the server, and reading logs means SSH.** No logs are shipped anywhere
except Sentry events. If the Lightsail instance is lost, its logs go with it. To read
logs, someone has to SSH in and know to look in three places: `logs/hci.log`,
`journalctl -u gunicorn`, and `/var/log/caddy/access.log`. The logs contain personal
data (for example, `auth_/backends.py` logs curator emails when it links Clerk
accounts), so how long we keep them should be a choice we make on purpose.

The goal is one obvious place to read app logs, rotation and retention we chose on
purpose, one retention policy for every process, no files created as a side effect of
loading settings, and a short documented way to read logs without guessing where they
are.

## The Technical Plan

**Make journald the one place for app logs.** Remove the `file` handler, and the code
that creates the directory and file, from `prod.py`. Keep the `console` handler, and
give it a format that includes the logger name (`{levelname} {name} {message}`).
journald already adds the time, host, unit, and PID to each line, so we don't repeat
them. After this, Django, Gunicorn, deploy-time management commands (their output shows
up in the Ansible and GitHub Actions log), and the backup timer from plan 004 all log
through the same channel. journald handles multiple processes, rotation, and retention.
`journalctl -u gunicorn --since "1 hour ago"` is the standard way to read logs, and it
can filter by time, unit, and priority.

**Set journald retention on purpose.** Ansible places a drop-in,
`/etc/systemd/journald.conf.d/hci.conf`, setting `Storage=persistent`,
`SystemMaxUse=1G`, and `MaxRetentionSec=90day`, then restarts `systemd-journald`. Ninety
days matches the backup retention in plan 004 and the Caddy default. It's long enough to
look into problems reported weeks later, and short enough that we don't keep personal
data forever.

**Write down Caddy's rotation.** Add `roll_size`, `roll_keep`, and `roll_keep_for` to
the Caddyfile's `log` block with the values we want, instead of relying on defaults. We
keep Caddy's access log as a JSON file (not journald) because fail2ban reads it, and
plan 002's filter expects that format and path. Also check how Caddy is run. If the
packaged `caddy.service` works, switch `caddy_start.yml` to `ansible.builtin.systemd`
with `state: reloaded`/`started` and `enabled: true`, so Caddy starts on boot, reloads
cleanly, and sends its runtime logs to journald.

**Make logs easy to read.** Add `just` recipes that run `journalctl` and `tail` on a
server through Ansible's ad hoc `command` module (using the inventory and SSH keys
already set up for the other `server-*` recipes). Document them in `docs/how-to.md`.

**Keep Sentry as the alerting layer.** We don't add a new tool for alerts. We make
Sentry's `LoggingIntegration` levels explicit in `base.py`, so it's clear from the code
that `ERROR` records alert, and we confirm that alert rules exist in the Sentry project
(Open Question 3). Shipping every log line off the server is optional (Open Question 2).

## Alternatives

**Keep the file and fix rotation.** Swap `RotatingFileHandler` for `WatchedFileHandler`
and let `logrotate` rotate `logs/hci.log` daily with a 90-day `rotate` count. That
gives time-based retention and is safe across processes. But it still stores every line
twice (file and journal), it adds a logrotate config, and it leaves two places to look.
It's only worth doing if someone needs plain files, for example to hand to another tool.

**Structured (JSON) app logs.** A JSON formatter (for example, `python-json-logger`)
would make app logs as machine-readable as Caddy's. That pays off once logs go to a
system that indexes fields. With journald and `grep` or `journalctl -g`, plain text is
easier to read, so this waits for Open Question 2.

**Ship logs off the server.** Options, from least to most setup:

- **Sentry Logs.** Set `enable_logs=True` in `sentry_sdk.init` and have the logging
  integration send `INFO` or `WARNING` and above. It uses a vendor and SDK we already
  have, puts logs next to the errors they explain, and needs no agent. The costs are
  Sentry quota and pricing, and personal data leaving our servers (though
  `send_default_pii=True` already sends some).
- **AWS CloudWatch Logs** through the CloudWatch agent reading journald. It's in the
  same AWS account, but it needs an agent and an IAM user (Lightsail has no instance
  roles), and `docs/design.md` already turned down CloudWatch for monitoring as too much
  overhead.
- **A hosted log service** (Better Stack, Papertrail, Grafana Cloud Loki) through a
  journald forwarder. It works well, but it's a new vendor and account for a small,
  low-traffic tool.

**Gunicorn access logs.** `--access-logfile -` would add a line per request to the
journal. Caddy already records every request with more detail (client IP, TLS, and
timing), so this would only add noise.

## Open Questions

1. **Is journald as the single place for app logs acceptable?** The plan's direction
   depends on this. The main alternative is keeping `hci.log` with logrotate (see
   Alternatives). This blocks Step 1 and Step 2.
2. **Should logs also go off the server, and if so, where?** The recommendation is to
   start without it (journald plus Sentry errors), then try Sentry Logs if SSH-based
   reading turns out to be painful or if we need logs to survive losing the instance.
   This blocks Step 5 only.
3. **Do the Sentry projects have alert rules that notify someone?** We can't see this
   from the repo. The user should check that new issues in production (`SENTRY_ENV`
   for prod) send email or Slack alerts. This doesn't block code. It's a manual check,
   listed in Step 4.
4. **How long should logs be kept?** The plan uses 90 days and a 1 GB cap for journald,
   and 90 days for Caddy. The logs contain curator emails and Clerk IDs, so there may be
   an institutional retention rule. This blocks the numbers in Step 2 and Step 3. The
   work can proceed with the defaults and change them later.
5. **What should happen to the old `logs/` directory on the servers?** The plan leaves
   the old `hci.log*` files alone and removes them by hand after the retention period.
   An Ansible task could delete them at once instead. This blocks nothing.

## Detailed Implementation

### Step 1 — Log to stderr only in production

#### `src/config/tests.py` — create

Write the tests first. Import `config.settings.prod` with `importlib`, with
`sentry_sdk.init` patched out (`unittest.mock.patch`) so the import doesn't
re-initialize Sentry with the real DSN from `.env`. Check that:

- No handler in `LOGGING["handlers"]` has a `class` ending in `FileHandler`.
- `LOGGING["root"]["handlers"] == ["console"]`.
- The console formatter's format string contains `{name}`.
- The module no longer defines `LOG_DIR` or `LOG_FILE`.

pytest already collects `tests.py` from anywhere under `src` (`pyproject.toml`).

#### `src/config/settings/prod.py` — modify

Delete `LOG_FILE_NAME`, `LOG_DIR`, `LOG_FILE`, and the code that makes the directory
and file, along with the `BASE_DIR` import if nothing else uses it. Remove the `file`
handler and the `verbose` formatter. Change the `simple` formatter to
`"{levelname} {name} {message}"`, and set `root.handlers` to `["console"]`. Add a
comment saying that stderr goes to journald through `gunicorn.service`, and point to
this plan.

#### `src/config/README.md` — modify

Update the `settings/prod.py` description (no more rotating file logger; console logs
go to journald on the servers). Add an entry for the new `tests.py`.

#### `.gitignore` — modify

Keep `logs/` for now, since developers may have old `logs/hci.log` files (there's one
in this checkout from June 2025). Add a comment saying the entry is only for old files.

### Step 2 — Set journald retention

#### `infra/ansible/tasks/placement/files/journald/hci.conf` — create

```
[Journal]
Storage=persistent
SystemMaxUse=1G
MaxRetentionSec=90day
```

#### `infra/ansible/tasks/placement/journald.yml` — create

Use `ansible.builtin.copy` with `become: true` to copy the file to
`/etc/systemd/journald.conf.d/hci.conf` (with `mode: "644"`, creating the directory
first with `ansible.builtin.file`). Follow `tasks/placement/fail2ban.yml`, and
`register` the result.

#### `infra/ansible/tasks/admin/journald_restart.yml` — create

Use `ansible.builtin.systemd` with `name: systemd-journald` and `state: restarted`, and
run it only when the placement task changed something.

#### `infra/ansible/playbooks/init.yml` and `deploy.yml` — modify

Include both tasks in each playbook. In `deploy.yml`, put them near the start, after
apt upgrade. They can be re-run safely, so existing servers pick up the config on their
next deploy. The deploy after Step 1 merges will also stop the servers writing
`logs/hci.log`, so Step 1 and Step 2 should ship close together (Step 2 first is fine).

Check with `just ansible-format-check` and `just ansible-lint`.

### Step 3 — Write down Caddy's log rotation and fix how Caddy runs

#### `infra/ansible/tasks/placement/files/templates/Caddyfile` — modify

Inside `output file /var/log/caddy/access.log { ... }`, add `roll_size 100MiB`,
`roll_keep 10`, and `roll_keep_for 2160h` (90 days, from Open Question 4). Keep
`format json` and the path as they are, because fail2ban's `caddy-blocked` filter needs
both.

#### `infra/ansible/tasks/admin/caddy_start.yml` — modify

First, SSH into the test server and run `systemctl status caddy` and `ps aux | grep
caddy` to see whether the packaged unit, the `caddy start` process, or both are
running. If the packaged unit can serve our Caddyfile (it runs `caddy run --config
/etc/caddy/Caddyfile`), replace the `command` task with `ansible.builtin.systemd`
(`name: caddy`, `enabled: true`, `state: started`) and add a separate
`caddy_reload.yml` (`state: reloaded`). Include `placement/caddy.yml` and
`caddy_reload.yml` in `deploy.yml`, so Caddyfile changes reach existing servers. Caddy's
runtime logs then go to journald (`journalctl -u caddy`). If the check turns up
something else, write it down in this plan before changing the task.

### Step 4 — Make Sentry's alerting explicit

#### `src/config/settings/base.py` — modify

Pass `integrations=[LoggingIntegration(level=logging.INFO,
event_level=logging.ERROR)]` to `sentry_sdk.init`. These are the current defaults, but
now they're visible in the code. Update the comment above `sentry_sdk.init` to say that
`ERROR` log records become Sentry issues.

#### `src/config/tests.py` — modify

Add a test that patches `sentry_sdk.init`, imports `config.settings.base` again, and
checks that it was called with a `LoggingIntegration` whose event level is
`logging.ERROR`.

#### Manual check (no file)

In the Sentry project, check that an issue alert rule notifies the team for the
production environment (Open Question 3). Write the result in `docs/design.md` under
"Error Monitoring and Uptime".

#### `src/config/README.md` — modify

Mention the explicit logging integration in the `settings/base.py` description.

### Step 5 — Optional: send logs to Sentry Logs

Do this only if Open Question 2 says so. In `base.py`, set `enable_logs=True` and give
the logging integration `sentry_logs_level=logging.WARNING` (or `INFO`). Keep
`test.py` calling `sentry_sdk.init()` with no arguments, so tests don't send anything.
Add a test like the one in Step 4. Update `src/config/README.md` and `docs/design.md`.

### Step 6 — Recipes and docs for reading logs

#### `justfile` — modify

In the Server group, add:

- `server-test-logs` and `server-prod-logs` (with `lines="200"`). They run
  `uv run ansible -i inventory.ini <group> -b -m ansible.builtin.command -a
  "journalctl -u gunicorn -n {{ lines }} --no-pager"` from `infra/ansible`.
- `server-test-caddy-logs` and `server-prod-caddy-logs`. They run `tail -n {{ lines }}
  /var/log/caddy/access.log`.

Follow the comment style of the existing recipes.

#### `docs/how-to.md` — modify

Add "How to Read Production Logs". Cover the recipes; useful `journalctl` flags
(`--since`, `-p warning`, `-g <pattern>`, `-u hci-backup` once plan 004 lands); where
Caddy's access log is and that fail2ban reads it; how to check fail2ban bans
(`sudo fail2ban-client status caddy`); and that errors show up in Sentry. Also say that
logs are kept 90 days and hold personal data.

#### `docs/design.md` — modify

Add a short "Logging" item under Cross-Cutting Concerns: journald for the app, Caddy
JSON for access logs, and Sentry for alerts.

## Sources

- Notes: "HCI: Think about a better system for logs — Right now, I believe we write
  logs to a file in production. Do we do anything else? Do we rotate log files?"
- `docs/plans/002-bot-protection.md` (Caddy JSON access log read by fail2ban)
- `docs/plans/004-backup-and-restore.md` (backup timer that logs to journald)
