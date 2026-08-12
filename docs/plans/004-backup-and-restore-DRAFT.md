# Database Backup and Restore

## Overview

The system will have two backup tiers: a pre-deployment backup taken automatically before
every production deploy, and a daily scheduled backup taken at a fixed time each night.
Both go to S3. A weekly scheduled job restores the latest production backup to the test
environment and runs a smoke check to verify the backup is valid and restorable. If
anything goes wrong in production, there is a documented runbook for restoring and
recovering.

## AWS Setup

You will need a dedicated S3 bucket for backups and an IAM user with a minimal policy
granting only the actions django-dbbackup needs: listing the bucket, uploading objects,
downloading objects, and deleting objects. The IAM credentials get stored as secrets in
GitHub (for use in Actions) and as environment variables on the production server (for use
by django-dbbackup at runtime). The bucket should have a lifecycle rule configured to
automatically delete objects older than 90 days. No versioning is needed — the naming
conventions described below make individual backups identifiable without it.

To keep pre-deployment and daily backups visually distinct and easy to locate, store them
under separate S3 key prefixes: `pre-deployment/` and `daily/`. This becomes important
during a recovery when you need to quickly find the backup that corresponds to a specific
commit.

## django-dbbackup Configuration

Install django-dbbackup and add it to `INSTALLED_APPS`. Configure it to use S3 as its
storage backend, pointed at your bucket and using the AWS credentials from the
environment. Since the production database is SQLite, the backup is essentially a copy of
the database file, which django-dbbackup wraps with compression and uploads to S3.

## Pre-Deployment Backup

The Ansible deploy playbook currently runs in this order: apt update, apt upgrade, git
pull, capture git SHA, uv sync, bun install, django migrate, collectstatic, gunicorn
restart.

The backup task belongs between "capture git SHA" and "django migrate." At that point in
the playbook, you have already pulled the new code and know the SHA you are about to
deploy. Taking the backup here gives you a snapshot of exactly what the database looked
like before that commit's changes took effect.

The backup filename should embed the git SHA so it is findable later. Something like
`pre-deployment-<sha>-<timestamp>.dump` stored under the `pre-deployment/` prefix.
django-dbbackup supports specifying an output filename via a command-line argument, so the
Ansible task can construct the filename using the captured SHA variable.

Critically, if the backup task fails, the playbook must stop. A deploy without a
successful backup removes your safety net. Configure the Ansible task to fail the play on
error rather than continuing.

## Daily Backup

Set up a cron job on the production server that runs `python manage.py dbbackup` once per
day, in the early morning when traffic is lowest. The output goes to the `daily/` prefix
in S3 with a timestamp-based filename (django-dbbackup's default behavior). This cron job
should be provisioned via Ansible as part of your server setup, not the deploy playbook —
it is infrastructure configuration, not a deployment step.

The daily backup covers the scenario where a bug silently corrupts data over hours or days
after a deploy, making the pre-deployment backup insufficient as a restore point.

## Weekly Restore Test

Add a scheduled GitHub Actions workflow that runs once a week. It should:

1. Download the most recent daily backup from the `daily/` prefix in S3
2. SSH into the test server and restore it using `python manage.py dbrestore`
3. Run `python manage.py migrate --check` to confirm the restored schema matches the
   current codebase
4. Make an HTTP GET request to a public repo page and assert a 200 response
5. Report failure via GitHub Actions' built-in email notification if any step fails

One subtlety worth noting: the test server runs whatever code is on its current branch,
and the prod backup reflects prod's schema. If prod and test have diverged significantly
— for example, if test has migrations that prod does not — `migrate --check` will fail for
reasons unrelated to backup validity. This is acceptable; a failure still warrants
investigation. But it means the smoke check conflates "backup is valid" with "schemas are
in sync," and failures should be interpreted with that in mind.

## Restore Runbook

When something goes wrong in production:

1. Identify the SHA of the bad commit.
2. Find the corresponding pre-deployment backup in S3 under `pre-deployment/` — it will
   have the SHA in the filename.
3. SSH into the production server and restore the backup with `python manage.py dbrestore`.
4. Once the restore is confirmed, push a `git revert <bad-sha>` to main.
5. The CI/CD pipeline will run, deploy the reverted code, run `migrate` (which will be a
   no-op since the DB was restored and the migration file was reverted), and restart
   gunicorn.
6. Verify the application is serving correctly.

The order of steps 3 and 4 matters — restore the database before deploying the reverted
code. During the window between the DB restore and the revert deploy completing, the
application will be in a degraded state. This is acceptable.

If the data corruption happened well after the deploy and the pre-deployment backup is too
stale, fall back to the daily backups and restore the most recent one taken before the
corruption began.
