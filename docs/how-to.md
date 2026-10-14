# How-To Guides

## How to Create and Destroy Cloud Infrastructure

- Configure your AWS credentials using the `~/.aws/credentials` file or using
  environment variables. See the AWS docs for more information.

- Install [Terraform](https://developer.hashicorp.com/terraform) if you don't have it
  installed.

- Go to the Terraform directory:

  ```
  cd infra/terraform
  ```

- If you don't have a `.terraform` directory, run:

  ```
  terraform init
  ```

- To see possible workspaces, run:

  ```
  terraform workspace list
  ```

- If you want to create or destroy infrastructure for the `foo` workspace, run:

  ```
  terraform workspace select foo
  ```

- If you want to create a new workspace named `bar`, run:

  ```
  terraform workspace new bar
  ```

- To create infrastructure, run:

  ```
  terraform apply
  ```

- To destroy infrastructure, run:

  ```
  terraform destroy
  ```

## How to Configure Backup Credentials

Each server backs up its database to its own S3 bucket. The bucket and the IAM users
that use it are created by `infra/terraform/backup.tf`. After you run `terraform apply`
in a workspace, give that workspace's server its credentials:

- In `infra/terraform`, select the workspace (`test` or `prod`) and read the outputs:

  ```
  terraform workspace select test
  terraform output backup_bucket_name
  terraform output backup_writer_access_key_id
  terraform output -raw backup_writer_secret_access_key
  ```

- SSH into that workspace's server and add these lines to the `.env` file in the root of
  the repository. Use `hci` for `SUBDOMAIN` on prod and `hci-test` on test. It's used in
  backup names.

  ```
  AWS_ACCESS_KEY_ID=<backup_writer_access_key_id>
  AWS_SECRET_ACCESS_KEY=<backup_writer_secret_access_key>
  DBBACKUP_BUCKET_NAME=<backup_bucket_name>
  SUBDOMAIN=hci-test
  ```

- Check that the server can reach the bucket. It should print "No backups found." or
  the backups taken so far, with no error. Use `list_backups`, not django-dbbackup's
  `listbackups`, which doesn't look under prefixes like `daily/`:

  ```
  cd ~/hla-curation-interface/src
  ~/.local/bin/uv run manage.py list_backups
  ```

Every deploy installs a systemd timer, `hci-backup.timer`, that backs up the database
under `daily/` every night at midnight Pacific. If a backup fails, it emails
`ALERT_EMAILS` (see How to Configure Email). To check the timer, SSH into the server and
run:

```
systemctl list-timers hci-backup.timer
journalctl -u hci-backup.service --since yesterday
```

To take a backup right away, run `sudo systemctl start hci-backup.service`.

Every Monday, the restore check workflow in GitHub Actions
(`.github/workflows/restore-check.yml`) restores the newest `daily/` prod backup on a
GitHub runner, applies `main`'s migrations, and checks that the site serves the
published curations. It fails if the newest backup is more than 48 hours old, which
catches a timer that stopped. GitHub emails you when it fails. To run it now, open the
workflow on GitHub's Actions tab and choose Run workflow.

The restore check reads prod backups with a separate, read-only user. In the `prod` workspace, read `backup_bucket_name`, `backup_reader_access_key_id`,
and `backup_reader_secret_access_key`, then add them to the repository's GitHub secrets
as `PROD_BACKUP_BUCKET_NAME`, `BACKUP_READER_AWS_ACCESS_KEY_ID`, and
`BACKUP_READER_AWS_SECRET_ACCESS_KEY`.

Lightsail also takes a snapshot of each server every day at 06:00 UTC and keeps the
last 7. A snapshot covers what the database backups don't, such as the hand-kept `.env`
and Caddy's certificates. Restoring one means building a new instance from it in the
Lightsail console, which replaces the whole server, so for database problems, restore a
database backup instead.

## How to Configure Email

Each server sends email, such as an alert when the nightly backup fails, through Amazon
SES. `infra/terraform/ses.tf` sets up SES to send from the server's own subdomain and
creates an IAM user that can only send email. After you run `terraform apply` in a
workspace:

- Wait a few minutes, then check that the subdomain shows as verified in the SES
  console's Identities page, in us-west-2. Its DKIM records are created for you.

- While SES is in the sandbox, it delivers only to verified addresses. In the SES
  console, choose Create identity, then Email address, and enter each address in
  `ALERT_EMAILS`. Each owner clicks the link that AWS emails them.

- Read the SMTP credentials:

  ```
  terraform workspace select test
  terraform output email_smtp_username
  terraform output -raw email_smtp_password
  ```

- SSH into that workspace's server and add these lines to the `.env` file in the root
  of the repository. Use `noreply@hci.clinicalgenome.org` on prod. Separate several
  alert addresses with commas.

  ```
  EMAIL_HOST_USER=<email_smtp_username>
  EMAIL_HOST_PASSWORD=<email_smtp_password>
  DEFAULT_FROM_EMAIL=noreply@hci-test.clinicalgenome.org
  ALERT_EMAILS=you@example.com
  ```

- Send a test alert, and check that it arrives:

  ```
  just server-test-send-test-alert
  ```

To email people who haven't verified their address, such as curators, request
production access for SES in the AWS console first.

## How to Set Up a Server for the First Time

- Create the cloud infrastructure for the server if you haven't already done so.

- Populate the `infra/ansible/inventory.ini` file.

- To set up the test site, run the following command from the root of the repository:

  ```
  just server-test-init
  ```

- To set up the production site, run the following command from the root of the
  repository:

  ```
  just server-prod-init
  ```

- If a task fails during initialization, it's usually easier to SSH in and fix it
  manually than to futz with Ansible tasks.

- Make sure the demographics fixtures are loaded.

- Make sure to add the Ansible SSH key to the `authorized_keys` file.

## How to Manually Deploy the HCI

The HCI's deployments are done by a GitHub Actions workflow. However, if you need to
manually deploy the HCI, follow the steps below.

- Create the cloud infrastructure for the server if you haven't already done so.

- Set up the server if you haven't already done so.

- To deploy the test site, run the following command from the root of the repository:

  ```
  just server-test-deploy
  ```

- To set up the production site, run the following command from the root of the
  repository:

  ```
  just server-prod-deploy
  ```

Every deploy, manual or not, backs up the database just before it migrates. The deploy
output prints the backup's name, for example:

```
Pre-deployment backup: pre-deployment/hci-3f2a9c1-to-88c5e47-2026-09-25T180102Z.sqlite3.gz
```

The first SHA is the code the backup's data matches, and the second is the code being
deployed. If the backup fails, the deploy stops before it migrates, so the server needs
its backup credentials first (see How to Configure Backup Credentials).

## How to Revert a Bad Deploy

Use this when a deploy broke the site or damaged data. Restoring the deploy's
pre-deployment backup puts the code and the data back to exactly where they were before
the deploy. Anything entered since the deploy is lost from the live site. That's
acceptable for the HCI, and the restore saves it in a pre-restore backup first, so you
can copy back anything someone needs by hand.

- Find the deploy's backup name. The deploy output prints it (in your terminal, or in
  the GitHub Actions log while continuous deployment exists):

  ```
  Pre-deployment backup: pre-deployment/hci-3f2a9c1-to-88c5e47-2026-09-25T180102Z.sqlite3.gz
  ```

  Or list the backups and pick the newest `pre-deployment/` one:

  ```
  just server-prod-list-backups
  ```

- Restore the backup and its "from" SHA, the first SHA in the name. Gunicorn is stopped
  while this runs, so the site is down for a minute or two:

  ```
  just server-prod-restore pre-deployment/hci-3f2a9c1-to-88c5e47-2026-09-25T180102Z.sqlite3.gz 3f2a9c1
  ```

- Check that the site's footer shows the "from" SHA (`3f2a9c1` above).

- Open a pull request that runs `git revert` on the bad commit, and merge it. Until it's
  merged, merge nothing else: the next deploy checks out `main` again, which would put
  the bad code back.

- If someone needs data entered after the bad deploy, it's in the `pre-restore/` backup
  that the restore printed. Restore that backup on your machine, not on the server, and
  copy what's needed back by hand.

To rehearse, run the same steps on the test server with `just server-test-list-backups`
and `just server-test-restore`.

## How to Restore After Data Corruption

Use this when data was damaged, for example by a bug, and you find out after the fact.

- List the backups and pick the newest one from before the damage. `daily/` backups are
  taken every night at midnight Pacific. `pre-deployment/` backups are taken before each
  deploy, and `manual/` backups by the admin's Back up now button.

  ```
  just server-prod-list-backups
  ```

- Restore it. If the code that's running now is the same as or newer than the code the
  backup came from, leave out the SHA: the restore runs `migrate`, which brings the
  schema up to date. Otherwise, pass the SHA that matches the backup.

  ```
  just server-prod-restore daily/hci-2026-10-14-000000.sqlite3.gz
  ```

- As with reverting a deploy, anything entered after the backup is in the `pre-restore/`
  backup that the restore printed.

If only the schema is damaged, for example by a bad migration, and the data is fine, you
can keep everything entered since the deploy by migrating back instead of restoring.
Check out the previous code and run `manage.py migrate <app> <previous_migration>` on
the server. This works only if every migration involved can be reversed.

If the restore fails partway, it leaves the site down on purpose, because serving code
that doesn't match the database is worse. Read the error in the output, fix the cause,
and run the same restore again. If it stopped because an `hci.db-journal` or
`hci.db-wal` file exists, SQLite crashed in the middle of a write. Move that file and
`hci.db` somewhere safe before you run the restore again; don't delete them until the
site works. To bring the site back up without restoring, SSH into the server and run:

```
sudo systemctl start gunicorn.socket gunicorn.service
```

## How to Backfill Publication Authors

Publications added before the HCI stored full author lists have no authors, so they
show "------" for Authors and search matches only their primary author. The
`backfill_publication_authors` command refreshes each of them from PubMed. That also
updates their title, primary author, and year. Each change shows on the publication's
history page.

- Deploy a version of the HCI that includes the command, and make sure its migrations
  have run.

- SSH into the server as `ubuntu`, then change to the app's `src` directory:

  ```
  cd ~/hla-curation-interface/src
  ```

- List the publications the command would refresh, without changing anything:

  ```
  ~/.local/bin/uv run manage.py backfill_publication_authors --dry-run
  ```

- Run the backfill:

  ```
  ~/.local/bin/uv run manage.py backfill_publication_authors
  ```

  The command waits between PubMed requests, so it takes a few minutes for a few
  hundred publications. It prints how many publications it updated and how many
  failed, and lists each failure.

- If any fail, run the command again later. It only retries publications that still
  have no authors. You can also refresh a single publication with the Refresh from
  PubMed button on its detail page.
