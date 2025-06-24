================
Reference Guides
================

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

mypy expects ignore comments to be exactly ``# type: ignore``, so we can't provide
justifications for them in the same line. Try to avoid using these. If you have to use
one, you can provide a justification on another line if you want to.

Here's an example:

.. code-block:: python

    service = FooService(client=client)  # type: ignore

---------------
Git Conventions
---------------

This reference guide describes how we use Git.

Trunk-Based Development
=======================

.. _trunk-based development: https://trunkbaseddevelopment.com/

We use `trunk-based development`_.

Branch Naming
=============

Branches should be named with an issue number followed by a brief description of the
branch's purpose. For example: ``123-fix-foobar``.

------------
The Core App
------------

The core app is where the home page and the pages found in the HCI's footer are housed.
It is also used to house modules that aren't app-specific. For example, it houses a
custom ``UserProfile`` model that extends the Django ``User`` model. This
``UserProfile`` model isn't specific to any app.

``core.admin``
==============

.. automodule:: core.admin
   :members:

``core.apps``
=============

.. automodule:: core.apps
   :members:

``core.crud``
=============

.. automodule:: core.crud
   :members:

``core.models``
===============

.. automodule:: core.models
   :members:

``core.urls``
=============

.. automodule:: core.urls
   :members:

``core.views``
==============

.. automodule:: core.views
   :members:

-----------------
The Datatable App
-----------------

The datatable app provides a reusable ``datatable`` view that provides an interactive
searchable, sortable, and filterable table. It uses HTMX for interactivity. The
searching, sorting, and filtering are done on the backend.

``datatable.templatetags.custom_filters``
=========================================

.. automodule:: datatable.templatetags.custom_filters
   :members:

``datatable.admin``
===================

.. automodule:: datatable.admin
   :members:

``datatable.apps``
==================

.. automodule:: datatable.apps
   :members:

``datatable.constants``
=======================

.. automodule:: datatable.constants
   :members:

``datatable.metadata``
======================

.. automodule:: datatable.metadata
   :members:

``datatable.models``
====================

.. automodule:: datatable.models
   :members:

``datatable.queries``
=====================

.. automodule:: datatable.queries
   :members:

``datatable.urls``
==================

.. automodule:: datatable.urls
   :members:

``datatable.views``
===================

.. automodule:: datatable.views
   :members:

----------------
The Firebase App
----------------

The firebase app houses code related to using Google's Firebase service for
authentication.

``firebase.apps``
=================

.. automodule:: firebase.apps
   :members:

``firebase.backends``
=====================

.. automodule:: firebase.backends
   :members:

``firebase.clients``
====================

.. automodule:: firebase.clients
   :members:

``firebase.crud``
=================

.. automodule:: firebase.crud
   :members:

``firebase.urls``
=================

.. automodule:: firebase.urls
   :members:

``firebase.views``
==================

.. automodule:: firebase.views
   :members:
