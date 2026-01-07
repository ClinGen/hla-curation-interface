============
Explanations
============

-------------------------------
Using WorkOS for Authentication
-------------------------------

.. note::
    The Django documentation tells us that: "authentication verifies a user is who they
    claim to be, and authorization determines what an authenticated user is allowed to
    do." Django uses the term "authentication" to refer to both tasks. We will follow
    this convention in this explanation.

Why are we using WorkOS for authentication?
===========================================

ClinGen has many services. None of these services use the same authentication system.
We want to have the same authentication system across different ClinGen services.
PharmGKB is also planning on using WorkOS. WorkOS also provides some niceties like
signing in with your Google or Microsoft account instead of the typical email and
password login. WorkOS handles a lot of the messy and difficult-to-implement aspects
of authentication and authorization.

---------
Using Bun
---------

What is Bun?
============

Bun is a JavaScript runtime similar to NodeJS and Deno.

Why are we using Bun?
=====================

We use Bun to track our JavaScript dependencies in ``package.json``, and we use Bun to
build these JavaScript dependencies. In some cases, we use Bun to copy the already-built
JavaScript dependencies from the ``node_modules`` directory into the ``static``
directory where Django takes over.

Bun is significantly faster than NodeJS and somewhat faster than Deno. Bun provides a
pleasant developer experience.
