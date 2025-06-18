============
Explanations
============

---------------------------------
Using Firebase for Authentication
---------------------------------

.. note::
    The Django documentation tells us that: "authentication verifies a user is who they
    claim to be, and authorization determines what an authenticated user is allowed to
    do." Django uses the term "authentication" to refer to both tasks. We will follow
    this convention in this explanation.

Why are we using Firebase for authentication?
=============================================

ClinGen has many services. None of these services use the same authentication system.
We want to have the same authentication system across different ClinGen services.
PharmGKB is also planning on using Firebase. Firebase also provides some niceties like
signing in with your Google or Microsoft account instead of the typical email and
password login. Firebase also handles sending password reset emails.

How does authentication with Firebase work?
===========================================

At a high level, here's what happens:

* The user navigates to the login page.
* The user clicks the "Sign in with Google" button or logs in with their email and
  password.
* On the frontend, JavaScript is used to get a token [#f1]_ from Firebase.
* On the frontend, JavaScript is used to send the token to the backend.
* The backend verifies the token using the Firebase Admin SDK.
* The backend returns a response to the frontend.
* The frontend handles the response from the server.

How do we integrate Firebase with Django?
=========================================

Django has its own authentication system. However, Django allows you to customize the
authentication system. Django has a concept of "authentication backends." The default
authentication backend is ``django.contrib.auth.backends.ModelBackend``. To integrate
Firebase, we use a custom authentication backend.

.. rubric:: Footnotes

.. [#f1] These tokens are JSON Web Tokens.

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

What is the ``js`` directory for?
=================================

The ``js`` directory houses JavaScript modules that need to be built using Bun and then
copied into the ``static`` directory.
