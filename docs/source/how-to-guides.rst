=============
How-To Guides
=============

----------------------------------------------
How to Create and Destroy Cloud Infrastructure
----------------------------------------------

* Configure your AWS credentials using the ``~/.aws/credentials`` file or using
  environment variables. See the AWS docs for more information.
* Install [Terraform](https://developer.hashicorp.com/terraform) if you don't have it
  installed.
* ``cd infra/terraform``
* If you don't have a ``.terraform`` directory, run ``terraform init``.
* Run ``terraform workspace list`` to see possible workspaces.
* If you want to create or destroy infrastructure for the ``foo`` workspace, run
  ``terraform workspace select foo``.
* If you want to create a new workspace named ``bar``, run
  ``terraform workspace new bar``.
* To create infrastructure, run ``terraform apply``.
* To destroy infrastructure, run ``terraform destroy``.

-----------------------------------------
How to Set Up a Server for the First Time
-----------------------------------------

* Create the cloud infrastructure for the server if you haven't already done so.
* Populate the ``infra/ansible/inventory.ini`` file.
* From the root of the repository, run ``just server-test-init`` for the test site or
``just server-prod-init`` for the production site.

------------------------------
How to Manually Deploy the HCI
------------------------------

The HCI's production deployments are done by a GitHub Actions workflow. The HCI's test
site deployments are done manually. Follow the steps below to deploy the HCI's test
site. (The steps for a production deployment are similar, if you ever need to do a
manual production deployment.)

* Create the cloud infrastructure for the server if you haven't already done so.
* Set up the server if you haven't already done so.
* From the root of the repository, run ``just server-test-deploy`` for the test site or
  ``just server-prod-deploy`` for the production site.
