# Provide a simple way to run commands for this project.
#
# This file also documents command line "recipes" for this project. In order to use it,
# you must install the `just` program: https://github.com/casey/just.
#
# NOTE: For the sake of simplicity, we assume the user of this justfile is invoking the
# recipes from the root of the repository.

#=======================================================================================
# Pre-Commit Recipe
#=======================================================================================

# Run all code quality checks and tests.
pre-commit: qual-all test-all
alias pre := pre-commit

#=======================================================================================
# Code Quality Recipes
#=======================================================================================

# Run all code quality checks.
qual-all: qual-format-check qual-lint qual-type-check
alias qal := qual-all

# Format the code.
qual-format:
    uv run ruff format
    cd infra/terraform && terraform fmt
    yamlfmt
alias qfm := qual-format

# Check the code for formatting issues.
qual-format-check:
    uv run ruff format --check
    cd infra/terraform && terraform fmt -check
    yamlfmt -lint
alias qfc := qual-format-check

# Check the code for lint errors.
qual-lint:
    uv run ruff check
    cd infra/terraform && terraform validate
    cd infra/ansible && ansible-lint
    cd .github && uv run yamllint .
alias qlt := qual-lint

# Try to fix lint errors.
qual-lint-fix:
    uv run ruff check --fix
    cd infra/ansible && ansible-lint --fix
alias qlf := qual-lint-fix

# Check Python type hints.
qual-type-check:
    cd src && uv run pyright .
alias qtc := qual-type-check

#=======================================================================================
# Test Recipes
#=======================================================================================

# Run all tests.
test-all:
    cd src && uv run pytest
alias tal := test-all

# Run unit tests.
test-unit:
    cd src && uv run pytest -m unit
alias tun := test-unit

# Run component tests.
test-component:
    cd src && uv run pytest -m component
alias tcm := test-component

# Run integration tests.
test-integration:
    cd src && uv run pytest -m integration
alias tin := test-integration

# Run contract tests.
test-contract:
    cd src && uv run pytest -m contract
alias tcn := test-contract

# Run end-to-end tests.
test-e2e:
    cd src && uv run pytest -m e2e
alias tee := test-e2e

#=======================================================================================
# Coverage Recipes
#=======================================================================================

# Collect test coverage stats.
coverage-collect:
    cd src && uv run coverage run -m pytest
alias ccl := coverage-collect

# Print test coverage stats.
coverage-report:
    cd src && uv run coverage report
alias crp := coverage-report

# Build the test coverage site.
coverage-build-html:
    cd src && uv run coverage html
alias cbh := coverage-build-html

# Open the coverage site in your browser.
coverage-open-html:
    open src/htmlcov/index.html
alias coh := coverage-open-html

#=======================================================================================
# Docs Recipes
#=======================================================================================

# Build the developer documentation site.
docs-build-html:
    cd docs && uv run make html
alias dbh := docs-build-html

# Open the developer documentation site in your browser.
docs-open-html:
    open docs/build/html/index.html
alias doh := docs-open-html

#=======================================================================================
# Django Recipes
#=======================================================================================

# Inspect the project for common problems.
django-check:
    cd src && uv run manage.py check
alias djch := django-check

# Make migrations.
django-makemigrations:
    cd src && uv run manage.py makemigrations
alias djmm := django-makemigrations

# Apply migrations.
django-migrate:
    cd src && uv run manage.py migrate
alias djmi := django-migrate

# Run the development server.
django-runserver:
    cd src && uv run manage.py runserver
alias djru := django-runserver

# Enter the shell.
django-shell:
    cd src && uv run manage.py shell
alias djsh := django-shell

#=======================================================================================
# Server Recipes
#=======================================================================================

# Set up the test server for the first time.
server-test-init:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/init.yml --limit test_server
alias stei := server-test-init

# Set up the production server for the first time.
server-prod-init:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/init.yml --limit prod_server
alias spri := server-prod-init

# Deploy latest changes to the test server.
server-test-deploy:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/deploy.yml --limit test_server
alias sted := server-test-deploy

# Deploy latest changes to the production server.
server-prod-deploy:
    cd infra/ansible && uv run ansible-playbook -i inventory.ini playbooks/deploy.yml --limit prod_server
alias sprd := server-prod-deploy
