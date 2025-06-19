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
# Pre-Commit Recipe
#=====================================================================

# Runs all checks and tests. -----------------------------------------
pre-commit: src-all test-all infra-all
alias pre := pre-commit

#=====================================================================
# Continuous Integration Recipe
#=====================================================================

# Run all checks and tests that are run in CI. -----------------------
continuous-integration: py-format-check js-format-check py-lint js-lint py-type-check django-check django-collectstatic test-all
alias ci := continuous-integration

#=====================================================================
# Python Recipes
#=====================================================================

# Run all Python code quality checks. --------------------------------
py-all: py-format-check py-lint py-type-check
alias pyal := py-all

# Format the Python code. --------------------------------------------
py-format:
    uv run ruff format
alias pyfm := py-format

# Check the Python code for formatting issues. -----------------------
py-format-check:
    uv run ruff format --check
alias pyfc := py-format-check

# Check the Python code for lint errors. -----------------------------
py-lint:
    uv run ruff check
alias pylt := py-lint

# Try to fix lint errors in the Python code. -------------------------
py-lint-fix:
    uv run ruff check --fix
alias pylf := py-lint-fix

# Check Python type hints. -------------------------------------------
py-type-check:
    cd src && uv run mypy .
alias pytc := py-type-check

#=====================================================================
# JavaScript Recipes
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
# Combined Source Code Recipes
#=====================================================================

# Run all source code checks. ----------------------------------------
src-all: src-format-check src-lint src-type-check src-build
alias sal := src-all

# Format the source code. --------------------------------------------
src-format: py-format js-format
alias sfm := src-format

# Check the source code for formatting issues. -----------------------
src-format-check: py-format-check js-format-check
alias sfc := src-format-check

# Check the source code for lint errors. -----------------------------
src-lint: py-lint js-lint
alias slt := src-lint

# Try to fix lint errors in the source code. -------------------------
src-lint-fix: py-lint-fix js-lint-fix
alias slf := src-lint-fix

# Check source code types. -------------------------------------------
src-type-check: py-type-check
alias stc := src-type-check

# Run source code build steps. ---------------------------------------
src-build: js-build
alias sbl := src-build

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

# Collect new coverage, build new site, and open new site. -----------
coverage-new: coverage-clean coverage-collect coverage-build-html coverage-open-html
alias cnw := coverage-new

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
    open src/coverage/index.html
alias coh := coverage-open-html

# Remove test coverage artifacts. ------------------------------------
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

# Build new docs and open new docs. ----------------------------------
docs-new: docs-clean docs-build-html docs-open-html
alias dnw := docs-new

# Build the developer documentation site. ----------------------------
docs-build-html:
    cd docs && uv run sphinx-build source build
alias dbh := docs-build-html

# Open the developer documentation site in your browser. -------------
docs-open-html:
    open docs/build/index.html
alias doh := docs-open-html

# Remove the built documentation directory. --------------------------
docs-clean:
    rm -rf docs/build/
alias dcl := docs-clean

#=====================================================================
# Terraform Recipes
#=====================================================================

# Format the Terraform code. -----------------------------------------
terraform-format:
    cd infra/terraform && terraform fmt
alias tffm := terraform-format

# Check the Terraform code for formatting issues. --------------------
terraform-format-check:
    cd infra/terraform && terraform fmt -check
alias tffc := terraform-format-check

# Check the Terraform code for lint errors. --------------------------
terraform-lint:
    cd infra/terraform && terraform validate
alias tflt := terraform-lint

#=====================================================================
# Ansible Recipes
#=====================================================================

# Format the Ansible YAML. -------------------------------------------
ansible-format:
    cd infra/ansible && yamlfmt
alias anfm := ansible-format

# Check the Ansible YAML for formatting issues. ----------------------
ansible-format-check:
    cd infra/ansible && yamlfmt -lint
alias anfc := ansible-format-check

# Check the Ansible YAML for lint errors. ----------------------------
ansible-lint:
    cd infra/ansible && ansible-lint
alias anlt := ansible-lint

# Try to fix lint errors in the Ansible YAML. ------------------------
ansible-lint-fix:
    cd infra/ansible && ansible-lint --fix
alias anlf := ansible-lint-fix

#=====================================================================
# GitHub Actions Recipes
#=====================================================================

# Format the GitHub Actions YAML. ------------------------------------
gh-actions-format:
    cd .github && yamlfmt
alias ghfm := gh-actions-format

# Check the GitHub Actions YAML for formatting issues. ---------------
gh-actions-format-check:
    cd .github && yamlfmt -lint
alias ghfc := gh-actions-format-check

# Check the GitHub Actions YAML for lint errrors. --------------------
gh-actions-lint:
    cd .github && uv run yamllint .
alias ghlt := gh-actions-lint

#=====================================================================
# Combined Infrastructure as Code Recipes
#=====================================================================

# Run all infra code quality checks. ---------------------------------
infra-all: infra-format-check infra-lint
alias ial := infra-all

# Format the infra code. ---------------------------------------------
infra-format: terraform-format ansible-format gh-actions-format
alias ifm := infra-format

# Check the infra code for formatting issues. ------------------------
infra-format-check: terraform-format-check ansible-format-check gh-actions-format-check
alias ifc := infra-format-check

# Check the infra code for lint errors. ------------------------------
infra-lint: terraform-lint ansible-lint gh-actions-lint
alias ilt := infra-lint

# Try to fix lint errors in infra code. ------------------------------
infra-lint-fix: ansible-lint-fix
alias ilf := infra-lint-fix

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
