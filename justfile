# Provides a simple way to run commands for this project.
#
# This file also documents command line "recipes" for this project. In order to use it,
# you must install the `just` program: https://github.com/casey/just.
#
# To list the available recipes and what they do, invoke `just -l` at the command line.
# (The dashes after the comment describing the recipe are there to help the formatting
# of the output of the `just -l` command.)
#
# NOTE: For the sake of simplicity, we assume the user of this justfile is invoking the
# recipes from the root of the repository.

# Load the .env file before we run commands.
set dotenv-load := true

#=====================================================================
# Source Code Quality Recipes
#=====================================================================

# Run all source code quality checks. --------------------------------
qual-src-all: qual-src-format-check qual-src-lint
alias qsal := qual-src-all

# Format the source code. --------------------------------------------
qual-src-format:
    uv run ruff format
alias qsfm := qual-src-format

# Check the source code for formatting issues. -----------------------
qual-src-format-check:
    uv run ruff format --check
alias qsfc := qual-src-format-check

# Check the source code for lint errors. -----------------------------
qual-src-lint:
    uv run ruff check
alias qslt := qual-src-lint

# Try to fix lint errors in the source code. -------------------------
qual-src-lint-fix:
    uv run ruff check --fix
alias qslf := qual-src-lint-fix

#=====================================================================
# Django Recipes
#=====================================================================

# Inspect the project for common problems. ---------------------------
django-check:
    cd src && uv run manage.py check
alias djch := django-check

# Collect static files. ----------------------------------------------
django-collectstatic:
    cd src && uv run manage.py collectstatic
alias djcs := django-collectstatic

# Make migrations. ---------------------------------------------------
django-makemigrations:
    cd src && uv run manage.py makemigrations
alias djmm := django-makemigrations

# Apply migrations. --------------------------------------------------
django-migrate:
    cd src && uv run manage.py migrate
alias djmi := django-migrate

# Run the development server. ----------------------------------------
django-runserver:
    cd src && uv run manage.py runserver
alias djru := django-runserver

# Enter the shell. ---------------------------------------------------
django-shell:
    cd src && uv run manage.py shell
alias djsh := django-shell
