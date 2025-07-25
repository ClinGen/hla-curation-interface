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
Applications
------------

The HCI's code is split into applications with different responsibilities.

Core App
========

The core app is where the home page and the pages found in the HCI's footer are housed.
It is also used to house modules that aren't app-specific. For example, it houses a
custom ``UserProfile`` model that extends the Django ``User`` model. This
``UserProfile`` model isn't specific to any app. The core app's ``templates`` directory
has a ``common`` subdirectory containing partials that are used throughout the HCI.

Allele App
==========

The allele app handles the basic CRUD operations for alleles.

Haplotype App
=============

The haplotype app handles the basic CRUD operations for haplotypes.

Curation App
============

The haplotype app handles the basic CRUD operations for curations. It also handles
the basic CRUD operations for evidence, and code related to the scoring framework.

Datatable App
=============

The datatable app provides a reusable ``datatable`` view that provides an interactive
searchable, sortable, and filterable table. It uses HTMX for interactivity. The
searching, sorting, and filtering are done on the backend.

Publication App
===============

The publication app handles the basic CRUD operations for publications.
