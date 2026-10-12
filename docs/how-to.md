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
