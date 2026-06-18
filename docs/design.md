# HCI Design Doc

## Context and Scope

The HLA Curation Interface (HCI) is a web application built by the Stanford University
ClinGen team. It allows curators to record, score, and publish evidence-based
associations between HLA alleles or haplotypes and human diseases, using a structured
scoring framework.

The HCI manages five key objects — alleles, haplotypes, diseases, publications, and
curations — and a public-facing repository (HLArepo) of finalized curation records.
Access is restricted to users who have been granted curation permissions and have signed
an agreement not to store protected health information (PHI) in the HCI.

This document is intended for engineers who are new to the codebase and for product
owners who want to understand the system's architecture and key design decisions.

## Goals

- Provide curators with a structured data-entry interface that enforces the HLA scoring
  framework's rules and constraints.
- Maintain a complete, auditable change history for every record in the system.
- Publish finalized curations to HLArepo in a human-readable format (HTML).
- Publish finalized curations to HLArepo in a machine-readable format (JSON).
- Run reliably on minimal infrastructure; avoid cloud vendor lock-in.

## Non-Goals

- The HCI is not a public submission portal. All users must be manually granted access.
- The HCI does not host or mirror external databases (CAR, PubMed, Mondo); it fetches
  metadata from them at record-creation time and stores only what it needs.

## Design

### System Context

The HCI is a single Django application that integrates with several external systems:

**WorkOS** — SSO provider. The HCI delegates all authentication to WorkOS AuthKit and
verifies a sealed session cookie on each request.

**ClinGen Allele Registry (CAR)** — queried when a new allele is created to retrieve the
CAR ID for the given allele name.

**EBI Ontology Lookup Service (OLS)** — queried when a new disease is created to
retrieve the Mondo disease name and IRI.

**PubMed E-utilities / bioRxiv / medRxiv APIs** — queried when a new publication is
created to retrieve the title, primary author, and year.

All external calls happen synchronously at record-creation time. If an external API is
unavailable, the creation fails gracefully with an error; no background job queue is
involved.

### Application Architecture

The HCI is a standard Django monolith. There are no microservices, no task queues, and
no separate API layer. Server-rendered HTML templates are the primary UI delivery
mechanism.

This architecture was chosen deliberately to keep the stack simple and maintainable.
Rather than adopting a single-page application (SPA) framework, the HCI follows a
traditional multi-page application (MPA) pattern. HTMX is added where a small amount of
interactivity is needed, giving dynamic page updates without the overhead of a full
JavaScript framework. Python was a natural fit for the underlying language: the team is
already fluent in it, and it is widely used across the bioinformatics and biomedical
research communities.

**Key libraries:**

- **Web framework** — Django
- **WSGI server** — Gunicorn
- **Database** — SQLite
- **Static files** — WhiteNoise (compressed, fingerprinted)
- **Authentication** — WorkOS + custom `WorkOSBackend`
- **Audit history** — django-simple-history
- **Error monitoring** — Sentry
- **Frontend CSS** — Bulma
- **Partial page updates** — HTMX
- **Enhanced selects** — Choices.js
- **Sortable tables** — DataTables + jQuery

### Data Model

The core entities and their relationships:

- A **Curation** is typed as either allele-based or haplotype-based and has a single
  disease. It aggregates one or more evidence records and carries a computed total score
  and a classification.
- An **Evidence** record links a curation to a publication and holds all scored data
  fields (typing method, p-value, effect size, cohort size, etc.). It computes its own
  per-step scores; the curation sums them.
- A **PublishedCuration** is an append-only snapshot created when a curator marks a
  curation as done and publishes it to HLArepo.

All entities use zero-padded sequential slugs as human-readable identifiers (`A000001`,
`H000001`, `D000001`, `P000001`, `C000001`, `E000001`).

Every model carries full change history via `django-simple-history`.

### The Scoring Framework

Evidence records are scored across six steps that evaluate the quality and strength of
the association study. Each step maps field values to a numeric point contribution;
contributions are summed to produce a total score, which is compared against
classification thresholds to suggest a final classification.

The framework is defined in HLA framework paper. In the codebase it lives in
`src/curation/score.py` (per-step scoring functions), `src/curation/constants/score.py`
(point values and p-value/effect-size/cohort-size threshold intervals), and
`src/curation/constants/views.py` (the scoring matrix).

### Authentication and Authorization

All views except login and the WorkOS OAuth callback require a user to be both
authenticated and to hold curation permissions. This is enforced by `ProtectedViewMixin`
(for class-based views) and the `@protected_view` decorator (for function-based views),
both defined in `src/auth_/permissions.py`.

Two conditions must be satisfied before a user can access any protected view:

1. They must have signed the PHI agreement (`UserProfile.has_signed_phi_agreement`).
2. An admin must have granted them curation permissions
   (`UserProfile.has_curation_permissions`).

The `UserProfile.can_curate` property returns `True` only when both flags are set.

### Frontend Approach

The UI is fully server-rendered Django templates with no client-side routing. JavaScript
is used narrowly:

- **HTMX** — partial page updates (e.g. toggling field visibility on the Create
  Publication form based on publication type).
- **DataTables** — sortable, searchable tables on list pages.
- **Choices.js** — searchable multi-select and single-select inputs (e.g. the allele
  picker on the haplotype creation form).

Bulma provides the CSS framework. All JS and CSS dependencies are vendored under
`src/static/hci/` — there is no build step at runtime.

## Alternatives Considered

### AWS-Based Architecture (ECS + RDS)

An earlier design considered a more conventional cloud-native deployment: containers on
ECS, a managed PostgreSQL instance on RDS, secrets in Secrets Manager, and load
balancing via ALB.

This was rejected in favor of a single VPS running Gunicorn behind a reverse proxy with
a SQLite database. The reasons:

- **Cost** — a single VPS is substantially cheaper than the equivalent AWS stack for the
  traffic levels HCI sees.
- **Operational complexity** — a monolith on a VPS has a much smaller operational
  surface. There are no container registries, task definitions, or managed DB parameter
  groups to maintain.
- **Vendor independence** — the current setup can be migrated to any Linux host, or
  self-hosted entirely, without changes to the application code. SQLite in particular
  makes the database trivially portable.

The main trade-off is that the VPS is a single point of failure and vertical scaling is
the only option. For a low-traffic tool used by a small team of curators, this is an
acceptable constraint.

## Cross-Cutting Concerns

### PHI and Access Control

The PHI agreement gate and the curation-permissions gate are enforced at the view layer
on every request, not just at login time. This means revoking a user's permissions takes
effect immediately on their next request.

### Audit Trail

Every model uses `django-simple-history` to record a full change log. The history UI
(reachable from any entity's detail page) shows who changed what and when, with a
before/after field-level diff.

### External API Availability

The HCI depends on three external APIs at record-creation time (CAR, OLS, PubMed /
bioRxiv/medRxiv). If any of these are unavailable, the creation request fails and the
user is shown an error. There is no retry logic or fallback; the curator can try again
later. This is intentional — a record with missing metadata (e.g. no CAR ID on an
allele) would be misleading.

### Error Monitoring and Uptime

Sentry is initialized at application startup via `config/settings/base.py` and captures
all unhandled exceptions in both dev and production environments. Sentry was chosen for
its simple setup and generous free tier; a cloud-native alternative (e.g. AWS
CloudWatch) would have added cost and operational overhead that is not justified for
this tool.

UptimeRobot monitors the public URL and alerts the team if the service goes down.
