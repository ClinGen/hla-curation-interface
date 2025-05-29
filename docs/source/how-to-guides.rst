=============
How-To Guides
=============

----------------------------------------------
How to Create and Destroy Cloud Infrastructure
----------------------------------------------

.. _Terraform: https://developer.hashicorp.com/terraform

* Configure your AWS credentials using the ``~/.aws/credentials`` file or using
  environment variables. See the AWS docs for more information.

* Install `Terraform`_ if you don't have it installed.

* Go to the Terraform directory::

    cd infra/terraform

* If you don't have a ``.terraform`` directory, run::

    terraform init

* To see possible workspaces, run::

    terraform workspace list

* If you want to create or destroy infrastructure for the ``foo`` workspace, run::

    terraform workspace select foo

* If you want to create a new workspace named ``bar``, run::

    terraform workspace new bar

* To create infrastructure, run::

    terraform apply

* To destroy infrastructure, run::

    terraform destroy

-----------------------------------------
How to Set Up a Server for the First Time
-----------------------------------------

* Create the cloud infrastructure for the server if you haven't already done so.

* Populate the ``infra/ansible/inventory.ini`` file.

* To set up the test site, run the following command from the root of the repository::

    just server-test-init

* To set up the production site, run the following command from the root of the
  repository::

    just server-prod-init

------------------------------
How to Manually Deploy the HCI
------------------------------

The HCI's deployments are done by a GitHub Actions workflow. However, if you need to
manually deploy the HCI, follow the steps below.

* Create the cloud infrastructure for the server if you haven't already done so.

* Set up the server if you haven't already done so.

* To deploy the test site, run the following command from the root of the repository::

    just server-test-deploy

* To set up the production site, run the following command from the root of the
  repository::

    just server-prod-deploy

