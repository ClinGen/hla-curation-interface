# MVP TODOs

## We are using the new repo.

- [x] All checks and tests pass locally.
- [x] We've blown away old development migrations.
- [x] We've made the new repo.
- [ ] We've documented using Conventional Commits.
- [ ] We've documented our commit message conventions.
- [x] We've added our code to the new repo using Conventional Commits.
- [ ] We've set up CI in the new repo.
- [ ] We've set up a PR template.
- [ ] We've documented how we process issues.
- [ ] We've set up issue labels (critical, bug, feature, improvement).
- [ ] We've set up issue templates (critical, bug, feature, improvement).

## The app test deployed to the test server and the prod server.

- [x] The test server is running the HCI.
- [ ] The prod server is running the HCI.
- [ ] We have the following CI workflow: PR opened → checks pass → deploy to test.
- [ ] We have the following CI workflow: PR approved and merged → deploy to prod.
- [ ] We have the following CI workflow: PR approved and merged → deploy dev docs site.
- [ ] We have the following CI workflow: PR approved and merged → deploy test coverage report.

## The score calculator code is integrated.

- [ ] We've added the code to the code base.
- [ ] All checks and tests pass.
- [ ] We've recorded the to-do items for the score calculator.
- [ ] The score calculator is being used to calculate association scores.

## We're done refactoring.

- [x] Templates have been refactored to match routes as much as possible.
    - See [the routes test](./src/tests/integration/routes_test.py).
    - For example, `markers/new_allele.html` should be `markers/allele/new.html`.
    - [x] We've found all templates where this refactor is needed.
    - [x] We've made the changes.

- [x] Create an integration test that makes sure all routes return a 200 status code.

- [x] We no longer prepend includes with underscores.
- [x] Includes have been refactored to be inside their app namespace.
    - [x] We've found all templates where this refactor is needed.
    - [x] We've made the changes.

- [x] Views have been refactored.
    - For example, `views/new_allele.py` should be `views/allele.py`.
    - [x] We've found all views where this refactor is needed.
    - [x] We've made the changes.

- [x] Base classes have been created.
    - [x] We have a base class for clients.
    - [x] We have an ABC for views.
    - [x] We have an ABC for selectors.
    - [x] We have an ABC for services.

- [x] Selectors are in use.
    - [x] We've found all the read-only logic.
    - [x] We've made the changes.

- [x] Services are in use.
    - [x] We've found all the CUD logic.
        - [x] We've made the changes.

- [ ] Base classes are in use.
    - [ ] Clients implement their base class.
        - [x] diseases/mondo
        - [x] markers/allele
        - [ ] publications/pubmed
    - [x] Entity views implement their ABC.
        - [x] diseases/mondo
        - [x] markers/allele
        - [x] publications/pubmed
    - [x] Selectors implement their ABC.
    - [x] Services implement their ABC.

- [ ] We've renamed things that need to be renamed.
    - [ ] We've replaced instances of "all" with "list."
    - [ ] We've replaced instances of "overview" with "details."
    - [ ] We've replaced instances of "allele" with "HLA allele."

## We're handling errors as best we can.

- [ ] We've documented our error handling conventions.
- [ ] We've located parts of the code base that need improved error handling.
- [ ] We're handling errors in the parts of the code base we located.
- [ ] We've identified existing tests that need to be modified.
- [ ] Existing tests take error handling into consideration.

## We're logging where necessary.

- [x] We've documented our error logging conventions.
- [ ] We've located parts of the code base that might need logs.
- [ ] We're logging in the parts of the code base we located.

## We have tests where necessary.

- [ ] We've documented our testing conventions.
- [ ] We've located modules missing tests.
- [ ] We've implemented missing tests.

## We're validating data.

- [ ] We've documented our data validation conventions.
- [ ] We've located places in the code that need data validation.
- [ ] We've implemented data validation.

## Docstrings are useful.

- [ ] We've identified stop-sign docstrings.
- [ ] We've fixed stop-sign docstrings.
- [ ] We've found docstrings that don't have arguments documented.
- [ ] We've documented all arguments.

## MVP functionality is complete.

- [ ] Models have a human-readable ID.
    - Ideas:
        - `AL`: denotes allele
        - `HP`: denotes haplotype
        - `ALC`: denotes allele curation
        - `HPC`: denotes haplotype curation
        - `ALA`: denotes allele association
        - `HPA`: denotes haplotype association

- [ ] The basic workflow for the app is in place.
    - [x] The user can sign up.
    - [ ] The user can log in.
    - [x] The user can log out.
        - [ ] When the user signs up, their curator object is created.
    - [ ] The user can view their curations on the home page.
    - [ ] The user can add a curation.
    - [x] The user can add a disease.
    - [x] The user can add a marker.
    - [x] The user can add a publication.
    - [ ] The user can view all curations.
    - [ ] The user can view all diseases.
    - [ ] The user can view all markers.
    - [x] The user can view all publications.
    - [ ] The user can curate.

- [ ] We have end-to-end tests for all workflows.
    - [ ] sign up
    - [ ] log in
    - [ ] log out
    - [ ] view all curations on the home page when logged out
    - [ ] view your curations on the home page when logged in
    - [ ] click all buttons on the home page
    - [ ] add a curation
    - [ ] add a disease
    - [ ] add a marker
    - [ ] add a publication
    - [ ] view all curations
    - [ ] view all diseases
    - [ ] view all markers
    - [ ] view all publications
    - [ ] curate

- [ ] We've decided on permissions.
- [ ] Permissions have been implemented.

## Nice-to-have tasks are complete.

- [ ] We have a footer in Ingrid's purple.
- [ ] The help text can be edited by non-developers.
- [ ] We've added Firebase.
