============
Explanations
============

Project Structure
=================

App Structure
-------------

::

   .
   ├── admin       # Configure admin site pages.
   ├── clients     # Interact with external data sources like APIs.
   ├── forms       # House form classes.
   ├── migrations  # House generated database migrations.
   ├── models      # House database models
   ├── permissions # Centralize access control logic.
   ├── schemas     # House code used to validate data from external sources.
   ├── selectors   # Centralize read logic.
   ├── services    # Centralize create, update, and delete logic.
   ├── static      # House static assets like images, CSS, and JavaScript.
   ├── templates   # House app-specific templates.
   └── views       # Centralize HTTP logic.
