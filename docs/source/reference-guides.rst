================
Reference Guides
================

------------
The Core App
------------

The core app is where the home page and the pages found in the HCI's footer are housed.
It is also used to house modules that aren't app-specific.

``core.views``
==============

.. automodule:: core.views
   :members:

----------------
Code Conventions
----------------

This reference guide describes the code conventions we follow in developing the HCI.
Lint rules enforce most of our conventions automatically, but
there are still some conventions to be aware of.

Comments
========

Don't write obvious comments. The image below shows what not to do.

.. image:: _static/stop-sign.jpg
   :width: 200px
   :alt: A picture of a stop sign with another sign pointing to it with the text: "This is a stop sign"

Docstring Comments
------------------

When you're reading code, whether the code is part of a module, class, or function, the
question you usually ask yourself is: "What does this code do?" The answer to that
question should be in the docstring.

The "top-level" docstring for a module, class, or function should almost always
be something along the lines of:

- "Provides a way to..."
- "Enables the..."
- "Configures a..."

TODO Comments
-------------

- Try to avoid writing these "I'll do it later" comments.
- There are lint rules set up to prevent TODO comments, so you have to jump through
  some hoops to get them into the code base.
- TODO comments *must* have an author.
- TODO comments *must* be accompanied by a link to a GitHub issue.

Here's an example:

.. code-block:: python

    # TODO(Liam): Fix the foo feature. Tracked in https://github.com/org/repo/issue/123.

Lint Ignore Comments
--------------------

If you ignore a lint rule, you *must* provide a justification for doing so. Generally
speaking, it's better to just fix the problematic code.

Here's an example:

.. code-block:: python

    from .base import (  # noqa: F401 (We don't care about unused imports in this context.)

Type Hint Ignore Comments
-------------------------

If you ignore type hints, you *must* provide a justification for doing so. Generally
speaking, it's better to just fix the problematic code.

Here's an example:

.. code-block:: python

    service = FooService(client=client)  # pyright: ignore[reportArgumentType] (We are using a mock client for our test.)

