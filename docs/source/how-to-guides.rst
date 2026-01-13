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

* If a task fails during initialization, it's usually easier to SSH in and fix it
  manually than to futz with Ansible tasks.

* Make sure the demographics fixtures are loaded.

* Make sure to add the Ansible SSH key to the ``authorized_keys`` file.

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


---------------------------------------
How to Manually Test Sign Up and Log In
---------------------------------------

Testing sign up and log in is tricky to automate because we use Firebase for
authentication. Here are the steps for testing sign up and log in manually.

* Navigate to the Firebase web console.
* Find the development instance.
* Delete your user accounts from the development instance.
* Run the HCI locally.
* Make sure you can sign up with email and password using a temporary email service.
* Log out of your temporary email account.
* Log into your temporary email account.
* Make sure you can sign up with a Google account.
* Log out of your Google account.
* Log into your Google account.
* Make sure you can sign up with a Microsoft account.
* Log out of your Microsoft account.
* Log into your Microsoft account.

----------------------------------------------
How to Manually Test Editing Your User Profile
----------------------------------------------

It's tricky to automate the testing of the of the user profile page because we use
Firebase for some of the functionality of the user profile page. Here are the steps for
testing the user profile page manually.

* Run the HCI locally.
* Create a new account.
* Navigate to the user profile page.
* Make sure you can resend the verification email.
* Make sure you can verify your email.
* Click the edit button.
* Make sure you can change your display name.
* Make sure you can reset your password.

---------------------------------------
How to Give a User Creation Permissions
---------------------------------------

* The user must have an account.
* An admin must mark the user's ``User`` object as active in the admin site.
* The user must have their email verified.
