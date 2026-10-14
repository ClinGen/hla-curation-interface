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

- Check that the server can reach the bucket. It should print an empty list, or the
  backups taken so far, with no error:

  ```
  cd ~/hla-curation-interface/src
  ~/.local/bin/uv run manage.py listbackups
  ```

The weekly restore check in GitHub Actions reads prod backups with a separate, read-only
user. In the `prod` workspace, read `backup_bucket_name`, `backup_reader_access_key_id`,
and `backup_reader_secret_access_key`, then add them to the repository's GitHub secrets
as `PROD_BACKUP_BUCKET_NAME`, `BACKUP_READER_AWS_ACCESS_KEY_ID`, and
`BACKUP_READER_AWS_SECRET_ACCESS_KEY`.

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
