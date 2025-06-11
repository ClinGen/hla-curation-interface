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
# Continuous Integration Recipe
#=====================================================================

# Run all checks and tests that are run in CI. -----------------------
continuous-integration: qual-src-format-check qual-src-lint django-check test-all
alias ci := continuous-integration

#=====================================================================
# Source Code Quality Recipes
#=====================================================================

# Run all source code quality checks. --------------------------------
qual-src-all: qual-src-format-check qual-src-lint qual-src-type-check
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

# Check Python type hints. -------------------------------------------
qual-src-type-check:
    cd src && uv run mypy .
alias qstc := qual-src-type-check

#=====================================================================
# JavaScript Code Recipes
#=====================================================================

# Run all JavaScript checks. -----------------------------------------
js-all: js-format-check js-lint
alias jal := js-all

# Format JavaScript code. --------------------------------------------
js-format:
    bunx biome format --write .
alias jsfm := js-format

# Check the JavaScript code for formatting issues. -------------------
js-format-check:
    bunx biome format .
alias jsfc := js-format-check

# Check the JavaScript code for lint errors. -------------------------
js-lint:
    bunx biome lint .
alias jslt := js-lint

# Try to fix lint errors in the JavaScript code. ---------------------
js-lint-fix:
    bunx biome lint --write .
alias jslf := js-lint-fix

# Build our JavaScript dependencies. ---------------------------------
js-build:
    bun build.js
alias jsbl := js-build

#=====================================================================
# Test Recipes
#=====================================================================

# Run all tests. -----------------------------------------------------
test-all:
    cd src && uv run manage.py test --shuffle
alias tal := test-all

#=====================================================================
# Coverage Recipes
#=====================================================================

# Collect test coverage stats. ---------------------------------------
coverage-collect:
    cd src && uv run coverage run --rcfile=../pyproject.toml manage.py test
alias cco := coverage-collect

# Print test coverage stats. -----------------------------------------
coverage-report:
    cd src && uv run coverage report --rcfile=../pyproject.toml
alias crp := coverage-report

# Generate test coverage XML. ----------------------------------------
coverage-xml:
    cd src && uv run coverage xml --rcfile=../pyproject.toml
alias cxm := coverage-xml

# Build the test coverage site. --------------------------------------
coverage-build-html:
    cd src && uv run coverage html --rcfile=../pyproject.toml
alias cbh := coverage-build-html

# Open the test coverage site in your browser. -----------------------
coverage-open-html:
    open src/htmlcov/index.html
alias coh := coverage-open-html

# Clean test coverage artifacts. -------------------------------------
coverage-clean:
    cd src && rm -rf coverage*
alias ccl := coverage-clean

#=====================================================================
# Django Recipes
#=====================================================================

# Inspect the project for common problems. ---------------------------
django-check:
    cd src && uv run manage.py check
alias djch := django-check

# Collect static files. ----------------------------------------------
django-collectstatic: js-build
    rm -rf src/public/
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

#=====================================================================
# Docs Recipes
#=====================================================================

# Build the developer documentation site. ----------------------------
docs-build-html:
    cd docs && uv run sphinx-build source build
alias dbh := docs-build-html

# Open the developer documentation site in your browser. -------------
docs-open-html:
    open docs/build/index.html
alias doh := docs-open-html

#=====================================================================
# Infrastructure Code Quality Recipes
#=====================================================================

# Run all infrastructure code quality checks. ------------------------
qual-infra-all: qual-infra-format-check qual-infra-lint
alias qial := qual-infra-all

# Format the infrastructure code. ------------------------------------
qual-infra-format:
    cd infra/terraform && terraform fmt
    yamlfmt
alias qifm := qual-infra-format

# Check the infrastructure code for formatting issues. ---------------
qual-infra-format-check:
    cd infra/terraform && terraform fmt -check
    yamlfmt -lint
alias qifc := qual-infra-format-check

# Check the infrastructure code for lint errors. ---------------------
qual-infra-lint:
    cd infra/terraform && terraform validate
    cd infra/ansible && ansible-lint
    cd .github && uv run yamllint .
alias qilt := qual-infra-lint

# Try to fix lint errors in the infrastructure code. -----------------
qual-infra-lint-fix:
    cd infra/ansible && ansible-lint --fix
alias qilf := qual-infra-lint-fix

#=====================================================================
# Server Recipes
#=====================================================================

# Set up the test server for the first time. -------------------------
server-test-init:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/init.yml --limit test_server
alias stei := server-test-init

# Set up the production server for the first time. -------------------
server-prod-init:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/init.yml --limit prod_server
alias spri := server-prod-init

# Deploy latest changes to the test server. --------------------------
server-test-deploy:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/deploy.yml --limit test_server
alias sted := server-test-deploy

# Deploy latest changes to the production server. --------------------
server-prod-deploy:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/deploy.yml --limit prod_server
alias sprd := server-prod-deploy
