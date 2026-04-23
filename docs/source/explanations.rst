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

Migrating to Clerk
==================

We are in the process of replacing WorkOS with Clerk. During the transition, both
backends live side by side. The ``AUTH_PROVIDER`` environment variable (``"workos"``
or ``"clerk"``) selects which flow is wired to the default ``/auth/login`` URL; the
Clerk flow also exists directly under ``/auth/clerk/login``, ``/auth/clerk/callback``,
and ``/auth/clerk/logout`` regardless of the flag.

The following environment variables configure the Clerk backend:

- ``CLERK_PUBLISHABLE_KEY``: The Clerk instance's publishable key.
- ``CLERK_SECRET_KEY``: The Clerk instance's secret key (used to verify session tokens
  and load user details from the Clerk Backend API).
- ``CLERK_SIGN_IN_URL``: The Clerk Account Portal sign-in URL for the instance (for
  example, ``https://accounts.<your-subdomain>.clerk.accounts.dev/sign-in``).
- ``CLERK_REDIRECT_URI``: Where Clerk should redirect users after a successful
  sign-in. In development this is ``http://127.0.0.1:8000/auth/clerk/callback``.
- ``CLERK_AUTHORIZED_PARTIES``: Optional comma-separated list of authorized origins
  to verify against the session token ``azp`` claim.

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
