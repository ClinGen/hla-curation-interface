================
Reference Guides
================

Code Conventions
================

This reference guide describes the code conventions we follow in developing the HCI.
Lint rules enforce most of our conventions automatically, but
there are still some conventions to be aware of.

Comments
--------

- Don't write obvious comments. The image below shows what not to do.

.. image:: _static/stop-sign.jpg
   :width: 200px
   :alt: A picture of a stop sign with another sign pointing to it with the text: "This is a stop sign"

Docstring Comments
^^^^^^^^^^^^^^^^^^

When you're reading code, whether the code is part of a module, class, or function, the
question you usually ask yourself is: "What does this code do?" The answer to that
question should be in the docstring.

The "top-level" docstring for a module, class, or function should almost always
be something along the lines of:

- "Provides a way to..."
- "Enables the..."
- "Configures a..."

Here are some general rules for docstrings:

- **Explain the purpose:** Instead of just saying what a function or class is, explain
  why it exists and what problem it solves.
- **Describe the behavior:** For functions and methods, detail what they do. What are
  the inputs, what processing occurs, and what are the outputs or side effects?
- **Clarify assumptions and constraints:** Are there any prerequisites for using this
  code? Are there limitations on the input or output?

TODO Comments
^^^^^^^^^^^^^

- Try to avoid writing these "I'll do it later" comments.
- There are lint rules set up to prevent TODO comments, so you have to jump through
  some hoops to get them into the code base.
- TODO comments *must* have an author.
- TODO comments *must* be accompanied by a link to a GitHub issue.

Here's an example:

.. code-block:: python

    # TODO(Liam): Fix the foo feature. Tracked in https://github.com/org/repo/issue/123.

Lint Ignore Comments
^^^^^^^^^^^^^^^^^^^^

If you ignore a lint rule, you *must* provide a justification for doing so.

Here's an example:

.. code-block:: python

    from .base import (  # noqa: F401 (We don't care about unused imports in this context.)

Type Hint Comments
^^^^^^^^^^^^^^^^^^

If you ignore type hints, you *must* provide a justification for doing so.

Here's an example:

.. code-block:: python

    service = MondoService(client=client)  # type: ignore (We are using a mock client for our test.)

Logs
----

Knowing where to log is important because clear and informative logs can be a
lifesaver when debugging.

During Request Handling
^^^^^^^^^^^^^^^^^^^^^^^

* **Entry and Exit Points of Views:** Log when a view function begins
  processing a request and when it finishes. Include details like the user (if
  authenticated), the requested URL, and the HTTP method.
* **Key Data Received in Forms:** When processing forms, log the important data
  submitted by the user. Be mindful of sensitive data and avoid logging it
  directly if not necessary.
* **Redirection Events:** Log when and where a user is redirected.

During Business Logic Execution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Start and End of Significant Processes:** For long-running tasks or crucial
  business logic functions, log when they start and finish. Include relevant
  identifiers or parameters.
* **Key Decisions and Branching:** Log which branch was taken and the data that
  influenced the decision.
* **Database Interactions:** You might want to log specific high-level database
  operations, especially when creating, updating, or deleting critical data. Be
  careful not to log sensitive data directly.

Error Handling and Exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Caught Exceptions:** Whenever you catch an exception, *always* log it using
  ``logger.exception()`` or ``logger.error(..., exc_info=True)`` to include the
  full traceback.

Security-Related Events
^^^^^^^^^^^^^^^^^^^^^^^

- **Authentication and Authorization:** Log successful and failed login
  attempts, user registration, and any authorization failures.
- **Changes to User Permissions or Roles:** If your application has user roles
  and permissions, log when these are modified.
