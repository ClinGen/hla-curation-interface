# Public HLArepo Site

## The Problem

HLArepo (the `repo` app, served at `/repo/`) is meant to be the public face of the HCI:
anyone should be able to browse published curations and download them as JSON without
an account. The repo views themselves are already public. None of
`PublishedCurationList`, `PublishedCurationDetail`, `PublishedCurationHistory`,
`PublishedCurationChange`, `download_all_json`, or `download_single_json` in
`src/repo/views.py` uses `ProtectedViewMixin` or `protected_view`, and there is no
site-wide login middleware in `src/config/settings/base.py`. The problem is that the
repo pages are wrapped in the curator UI, so a visitor who clicks almost anything ends
up on the Clerk sign-in page:

- Every repo template extends `src/templates/layouts/base.html`, which includes
  `src/templates/partials/navbar.html`. The navbar's Alleles, Haplotypes, Diseases,
  Publications, and Curations dropdowns all link to list and create views guarded by
  `ProtectedViewMixin`, which sends anonymous users to `LOGIN_URL` (`/auth/login`). The
  navbar also has a Log In button.
- `src/repo/templates/repo/detail.html` includes the curator partial
  `src/curation/templates/curation/partials/curation/detail_table.html`, which ends
  with a "View History" button that links to `curation-history`
  (`CurationHistory`, protected). The repo already has its own public History button
  right below it, so the page shows two history buttons, and one of them needs a login.
- The same page includes the evidence partial
  (`curation/partials/evidence/detail_table.html` under `src/curation/templates/`),
  which links every evidence ID to `evidence-detail` (`EvidenceDetail`, protected).
- The breadcrumbs on all four repo templates start at `home`, which is public but is
  the curator landing page. Its buttons link to the protected list and create views.
- `src/templates/partials/account_activation.html` shows the PHI and permissions notice
  to logged-in users who aren't curators, which makes no sense on a public page.

Issue #87 asks for the repo to be browsable with nothing that triggers a login. It also
asks how curators get back to the curation side. The maintainer said in the issue
comments that he is leaning toward giving HLArepo its own hostname (for example
`hlarepo.clinicalgenome.org`) instead of keeping it at `/repo/` on the HCI host. The
goal of this plan is to (1) give the repo a public layout with no login triggers,
which is needed either way, and (2) serve the repo on its own hostname from the same
Django process.

The comment on #87 also asks for MONDO links for diseases and CAR links for alleles and
haplotypes on the repo detail page. The user's notes add showing the evidence summary
in the repo. That *content* work is planned in the follow-up section of
`docs/plans/001-ep-review.md` and is out of scope here. This plan covers only access,
layout, and hosting.

## The Technical Plan

**A public layout.** We add a second root layout, `layouts/public.html`, for pages
anyone can see. It has the same assets and environment banner as `layouts/base.html`
but a small HLArepo navbar (brand, Search, Download All) and a public footer. It has no
Log In button, no curator dropdowns, and no account activation notice. The footer has
a plain "Curators: go to the HCI" link to the HCI home page, which is public. That
answers the "how do curators get back" question without putting a login on the page.
All four repo templates extend the new layout, and their breadcrumbs start at HLArepo
instead of HCI Home. The two shared curation partials get a `public` flag. When it is
set, they leave out the protected "View History" button and render evidence IDs as
plain text instead of links to `evidence-detail`. A test fetches every internal link on
each public page as an anonymous user and asserts that none of them redirects to the
login page, so we find out if a protected link comes back later.

**A separate hostname, same Django process.** The repo host and the HCI host are served
by the same Gunicorn and Django instance and the same SQLite database. Caddy gets a
second site address that proxies to the same Gunicorn socket and gets its own TLS
certificate automatically. Inside Django, a small middleware reads `request.get_host()`.
When the host is the repo host, it sets `request.urlconf = "config.urls_repo"`, a URL
configuration that mounts `repo.urls` at the root and nothing else. Setting
`request.urlconf` is a built-in Django feature, so we don't need a dependency like
`django-hosts`. When a request for `/repo/...` arrives on the HCI host, the middleware
returns a permanent redirect to the same path on the repo host, so existing links and
bookmarks keep working. Two settings, `REPO_BASE_URL` and `HCI_BASE_URL`, hold the
origins of the two sites. When `REPO_BASE_URL` is empty (the default, and the setting
in tests unless a test overrides it), the middleware does nothing and the app behaves
exactly as it does today, with the repo at `/repo/`. This means the code can be merged
and deployed before DNS exists.

Inside the repo host, `{% url %}` and `reverse()` resolve against `config.urls_repo`,
so links between repo pages work unchanged. Links that cross hosts (the HCI navbar's
HLArepo button, "View in HLArepo" on the curation detail page, the public footer's links
to About, Contact, and the HCI home page) go through two small helpers, `repo_reverse`
and `hci_reverse`, plus matching template tags. The helpers reverse against the right
URL configuration and add the right origin. Because `config.urls_repo` has no curator
URLs, the shared error templates (which extend `layouts/base.html` and reverse curator
URLs in the navbar) would raise `NoReverseMatch` on the repo host. So
`config.urls_repo` declares its own `handler400`, `handler403`, `handler404`, and
`handler500`, which render public-layout error pages.

**Sessions, CSRF, and Clerk.** We leave `SESSION_COOKIE_DOMAIN` and
`CSRF_COOKIE_DOMAIN` unset, so both cookies stay scoped to the host that set them.
Everyone is anonymous on the repo host, including curators who are logged in to the
HCI. That is intended: the repo is a read-only public site. The repo host has no POST
forms (search is an HTMX GET, downloads are GETs), so we don't need
`CSRF_TRUSTED_ORIGINS`. Clerk never loads on the repo host, so the Clerk dashboard
doesn't need a new domain. The one POST that the repo detail page has today, the
curator-only "Copy and Recurate" form, moves to the HCI curation detail page. That page
already has a "This curation has been published" notice, and a curator is logged in
there. For the same reason, `curation_publish` should redirect back to the curation
detail page (where the success message can be shown) instead of across hosts to
`repo-detail`, where the flash message would be lost.

**Infrastructure.** Terraform gets a second Route 53 A record per workspace pointing at
the existing Lightsail static IP. The Ansible inventory gets a `repo_subdomain`
variable next to `subdomain`. The Caddyfile template lists both addresses on the same
site block, so the bot-blocking matcher and JSON access log (which fail2ban reads) apply
to both. Caddy passes the original `Host` header through by default, which is what the
middleware needs. `ALLOWED_HOSTS` in `src/config/settings/prod.py` gets the two new
hostnames. Each server's `.env` gets `REPO_BASE_URL` and `HCI_BASE_URL`.

We don't know the hostname yet (see Open Questions), so the steps that depend on it are
blocked on that decision. Steps 1 and 2 (the public layout) are useful whatever we
decide and can ship first.

## Alternatives

**Keep HLArepo on the HCI host at `/repo/`, with only the public layout.** This is what
the issue originally asked for, and it is Steps 1 and 2 of this plan without Steps 4 to
6. It is less work: no DNS, no Caddy change, no host routing. Logged-in curators would
also keep seeing the "Copy and Recurate" button on the repo page. We don't recommend
stopping there. The public site would share an origin, cookies, and fail2ban jail with
the curator tool. Public URLs (which will be cited in papers and linked from other
ClinGen resources) would carry the `hci` name and be tied to the HCI's URL layout. And
curator UI could leak back into public pages through shared templates. A separate
hostname makes the boundary explicit and lets the repo change later (its own
deployment, caching, or a static export) without breaking public links. Because
`REPO_BASE_URL` defaults to empty, choosing this alternative only means skipping Steps
4 to 6. Nothing in Steps 1 and 2 needs to be undone.

**Use `django-hosts` for host-based routing.** `django-hosts` provides host-aware
`reverse` and `{% host_url %}` and handles the URL configuration switch. It would work,
but we only need one extra host. The built-in `request.urlconf` plus two small helper
functions does the same job without a dependency.

**Run the repo as a separate Django project or a static site.** A static export (render
the repo pages and JSON to files and serve them from Caddy or S3) would be the most
isolated and cacheable option. But it needs a build-and-publish step on every
publication, and history pages and search would have to be rebuilt without Django.
That's a lot of new machinery for the traffic we expect. Serving both hosts from one
process keeps the current single-server, single-database design from
`docs/design.md`.

## Open Questions

1. **Should HLArepo get its own hostname, and if so, which one?** The issue author
   wanted to keep the repo on the same site. The maintainer is leaning toward a separate
   host and suggested discussing it at a tool meeting. If we go ahead, we need both
   names: production (proposed `hlarepo.clinicalgenome.org`) and test (proposed
   `hlarepo-test.clinicalgenome.org`, matching `hci-test`). Blocks Steps 4, 5, and 6.
   If the answer is "same site", we close those beads and stop after Step 3.
2. **Should curator identities appear on public repo pages and in the public JSON?**
   The public history and change pages render `history_user` through `HistoryTable`
   and `common/history/change_body.html`. `serialize_published_curation` exports
   `published_by.username`. Since the move to Clerk, usernames are email addresses (see
   `ClerkBackend` in `src/auth_/backends.py`), so today these pages publish curator
   emails. Options: hide them, show a display name (first and last name), or keep them.
   Blocks Step 3.

## Detailed Implementation

### Step 1 — Public layout

#### `src/templates/layouts/public.html` — create

A root layout for public pages. Copy the `<head>` from `layouts/base.html`, but drop
`choices.min.js` and `choices.min.css`, which no public page uses, and the `hx-headers`
CSRF attribute, since public pages have no forms. The title prefix is "HLArepo |"
instead of "HCI |". The body includes `partials/env_banner.html`,
`partials/public_navbar.html`, `partials/messages.html`, `{% block main %}`, and
`partials/public_footer.html`. It must not include `partials/navbar.html` or
`partials/account_activation.html`.

#### `src/templates/partials/public_navbar.html` — create

A Bulma navbar with an "HLArepo" brand linking to `repo-search` and a "Download All
(JSON)" link to `repo-download-all`. Reuse the burger-menu script from
`partials/navbar.html`. Only link to `repo-*` URL names, so the navbar keeps working
under `config.urls_repo` in Step 4.

#### `src/templates/partials/public_footer.html` — create

The same logos, funding text, source link, and Git SHA as `partials/footer.html`, plus
the About, Contact, Citing, Help, Acknowledgements, and Collaborators links and a
"Curators: go to the HCI" link to `home`. For now these use `{% url %}`. Step 5 switches
them to `{% hci_url %}`. Consider pulling the shared logo and funding markup into a
partial that both footers include, so it doesn't drift.

#### `src/templates/README.md` — modify

Describe `layouts/public.html`, `partials/public_navbar.html`, and
`partials/public_footer.html`. Say in the `layouts/base.html` entry that it is the
curator layout.

### Step 2 — Repo pages use the public layout and don't link to protected pages

#### `src/repo/tests.py` — modify (write first)

Add a helper `assert_no_login_links(self, response)`. It extracts every `href` in the
response that starts with `/` (a small regex is enough), skips the logout link and
`/static/`, requests each one with a fresh anonymous `Client`, and asserts that none of
them redirects to a URL starting with `settings.LOGIN_URL`. Use it in new anonymous
tests for the list, detail, history, and change pages. The detail test's fixture must
have at least one `Evidence` row so the evidence table renders. Also add tests that, as
an anonymous user, each page `assertNotContains` the `id="log-out-button"`, the "Log
In" text, and `reverse("allele-list")`. Add one test that logs in a user without
curation permissions and asserts the account activation notice ("Account Activation")
is not rendered.

The existing `CopyButtonTest.test_copy_button_visible_for_curators` stays as-is in
this step. The button moves in Step 5.

#### `src/repo/templates/repo/{list,detail,history,change}.html` — modify

Extend `layouts/public.html`. Make HLArepo (`repo-search`) the root of the breadcrumbs
instead of `home`. In `detail.html`, pass `public=True` to both
`curation/partials/curation/detail_table.html` and
`curation/partials/evidence/detail_table.html`. Keep the existing History and Download
buttons. Keep the Copy and Recurate form behind its current
`request.user.profile.can_curate` check.

#### `src/curation/templates/curation/partials/curation/detail_table.html` — modify

Wrap the trailing "View History" button (which links to `curation-history`) in
`{% if not public %}`. The curator pages that include this partial
(`curation/detail.html`, `curation/review.html`, `curation/edit/evidence.html`) don't
pass `public`, so nothing changes for them.

#### `src/curation/templates/curation/partials/evidence/detail_table.html` — modify

When `public` is set, render the evidence slug as plain text instead of an
`evidence-detail` link, and never render the "Edit Evidence" button. Which evidence
columns and fields the public sees (including an evidence summary or a public evidence
detail page) belongs to the content follow-up in `docs/plans/001-ep-review.md`. If that
work creates repo-specific partials, it should keep the rule that public pages link
only to `repo-*` URLs, and the Step 2 test enforces it.

#### `src/curation/tests/test_views.py` — modify

Add a test that `CurationDetail` still renders the "View History" link and evidence
links for a curator, so the `public` flag doesn't regress the curator pages.

#### `src/repo/README.md`, `src/curation/README.md` — modify

Say that the repo templates extend the public layout. Document the `public` flag on the
two shared curation partials.

### Step 3 — Curator identity on public pages

Blocked by Open Question 2. If the answer is to hide identities or show a display name:

#### `src/repo/tests.py` — modify (write first)

Tests that the anonymous history page, the change page, and the output of
`download_single_json` don't contain the publisher's email, and that they contain the
agreed replacement (for example "------" or the user's full name).

#### `src/common/tables.py` — modify

Give `HistoryTable` a `hide_user` keyword argument (default `False`). When it is
`True`, exclude the `history_user` column (or render the display name, depending on
the answer). `PublishedCurationHistory` in `src/repo/views.py` passes
`hide_user=True`.

#### `src/common/templates/common/history/change_body.html` — modify

Wrap the "Changed By" row in `{% if not hide_user %}`, and have
`PublishedCurationChange` set `hide_user` to `True` in its context. The curator
history views don't set it, so they are unchanged.

#### `src/repo/serializers.py` — modify

Drop `published_by` from `serialize_published_curation`, or replace it with the display
name.

#### `src/common/README.md`, `src/repo/README.md` — modify

Document the new option and the serializer change.

### Step 4 — Host settings and routing

Blocked by Open Question 1.

#### `src/common/tests.py` — modify (write first)

Add `RepoHostMiddlewareTest`, which uses `override_settings(REPO_BASE_URL=
"http://hlarepo.testserver", HCI_BASE_URL="http://testserver", ALLOWED_HOSTS=[
"testserver", "hlarepo.testserver"])` and `self.client.get(path,
HTTP_HOST="hlarepo.testserver")`. Cases:

- `/` on the repo host renders `PublishedCurationList`.
- `/<slug>/detail` on the repo host renders the detail page.
- `/allele/`, `/admin/`, and `/auth/login` on the repo host return 404 and render the
  public-layout 404 template, not `404.html`.
- `/repo/<slug>/detail?x=1` on the HCI host returns 301 to
  `http://hlarepo.testserver/<slug>/detail?x=1`.
- With `REPO_BASE_URL=""`, `/repo/` on the HCI host renders the list, exactly as today.
- `repo_reverse("repo-detail", args=[slug])` and `hci_reverse("about")` return
  absolute URLs when the settings are set, and relative paths (`/repo/<slug>/detail`,
  `/about`) when they are empty.

#### `src/config/settings/base.py` — modify

Add `REPO_BASE_URL = os.getenv("REPO_BASE_URL", "")` and
`HCI_BASE_URL = os.getenv("HCI_BASE_URL", "")`, with a comment that an empty
`REPO_BASE_URL` means the repo is served at `/repo/` on the HCI host. Add
`"common.middleware.RepoHostMiddleware"` to `MIDDLEWARE` immediately *before*
`django.middleware.common.CommonMiddleware`. The `APPEND_SLASH` check in
`CommonMiddleware` reads `request.urlconf`, so it has to be set first. Add
`"common.context_processors.hosts"` to the context processors. For local testing,
document `REPO_BASE_URL=http://hlarepo.localhost:8000` and
`HCI_BASE_URL=http://localhost:8000` in `.env`. The dev setting `ALLOWED_HOSTS = []`
with `DEBUG = True` already allows `.localhost` subdomains.

#### `src/common/hosts.py` — create

`repo_host() -> str` (the netloc of `REPO_BASE_URL`, or `""`), `repo_reverse(viewname,
args=None, kwargs=None) -> str`, and `hci_reverse(viewname, args=None, kwargs=None) ->
str`. `repo_reverse` reverses with `urlconf="config.urls_repo"` and adds
`REPO_BASE_URL` when it is set. Otherwise it reverses with `urlconf="config.urls"`.
`hci_reverse` always reverses with `urlconf="config.urls"` and adds `HCI_BASE_URL`,
which may be empty. Use Google docstrings.

#### `src/common/middleware.py` — create

`RepoHostMiddleware`. If `settings.REPO_BASE_URL` is empty, it passes the request
through. If `request.get_host()` equals `repo_host()`, it sets
`request.urlconf = "config.urls_repo"`. Otherwise, if `request.path` starts with
`/repo/`, it returns `HttpResponsePermanentRedirect` to `REPO_BASE_URL` plus the path
without the `/repo` prefix, plus the query string.

#### `src/common/templatetags/hosts.py` — create

Simple tags `{% repo_url 'name' arg %}` and `{% hci_url 'name' arg %}` that wrap the
helpers.

#### `src/common/context_processors.py` — modify

Add `hosts(request)`, which returns `{"IS_REPO_HOST": ...}` so templates can tell which
site they are on if they need to.

#### `src/config/urls_repo.py` — create

`urlpatterns = [path("", include("repo.urls"))]`, plus `handler400`, `handler403`,
`handler404`, and `handler500` pointing to the views below.

#### `src/repo/views.py` — modify

Add `bad_request`, `permission_denied`, `page_not_found`, and `server_error`, each
rendering `repo/error.html` with the right status and message. `server_error` must not
depend on context processors that could themselves fail.

#### `src/repo/templates/repo/error.html` — create

Extends `layouts/public.html` and shows a status heading, a message, and a link back to
`repo-search`.

#### `src/common/README.md`, `src/config/README.md`, `src/repo/README.md` — modify

Document `hosts.py`, `middleware.py`, `templatetags/hosts.py`, the new context
processor, `urls_repo.py`, the new settings, and the error views and template.

### Step 5 — Cross-host links and moving curator actions

Blocked by Step 4.

#### Tests — modify (write first)

- `src/repo/tests.py`: with the repo host settings overridden, the detail page on the
  repo host never contains "Copy and Recurate", even for a user who is logged in on that
  host. Move `CopyButtonTest` into `src/curation/tests/test_views.py` and point it at
  `curation-detail` for a published curation. Run `assert_no_login_links` against the
  repo-host responses too.
- `src/curation/tests/test_views.py`: `curation_publish` redirects to `curation-detail`
  and the success message is in the next response. With the repo host settings
  overridden, "View in HLArepo" links to the absolute repo URL.
- `src/repo/tests.py`: `PublishedCuration.get_absolute_url()` returns the
  `repo_reverse` value in both modes.

#### `src/templates/partials/navbar.html` — modify

The HLArepo button uses `{% repo_url 'repo-search' %}`.

#### `src/templates/partials/public_footer.html` — modify

The About, Contact, Citing, Help, Acknowledgements, Collaborators, and "go to the HCI"
links use `{% hci_url %}`.

#### `src/curation/templates/curation/detail.html` — modify

"View in HLArepo" uses `{% repo_url 'repo-detail' object.slug %}`. Add the "Copy and
Recurate" form (moved from the repo detail page, same `curation-copy` POST and
`confirm()` prompt) inside the published notice, behind `can_curate`.

#### `src/repo/templates/repo/detail.html` — modify

Remove the Copy and Recurate form.

#### `src/curation/views.py` — modify

`curation_publish` redirects to `curation-detail` on success. The success message
includes a link to the repo record (built with `repo_reverse`) and the message tag
marks it safe, or the published notice on the detail page already provides the link.

#### `src/repo/models.py` — modify

`get_absolute_url` returns `repo_reverse("repo-detail", kwargs=...)`.

#### `src/{curation,repo,templates}/README.md` — modify

Record the moved button, the new link helpers in the templates, and the new redirect
target.

### Step 6 — DNS, TLS, and Caddy

Blocked by Open Question 1 and Step 4. This is operational. There are no Django tests,
but check the result on the test server first.

#### `infra/terraform/subdomain.tf` — modify

Add `aws_route53_record.repo`, an A record for the repo hostname in each workspace
(`prod` gets the production name, others get the test name). It points at
`aws_lightsail_static_ip.hci.ip_address` with `ttl = 300`.

#### `infra/ansible/inventory.ini` — modify

Add `repo_subdomain` to `[test_server:vars]` and `[prod_server:vars]`.

#### `infra/ansible/tasks/placement/files/templates/Caddyfile` — modify

Change the site address to
`{{ subdomain }}.clinicalgenome.org, {{ repo_subdomain }}.clinicalgenome.org`, so both
hosts share the log block, the `@blocked` matcher, and `reverse_proxy`. Caddy gets a
certificate for the new name automatically once DNS resolves. Deploy by re-running the
Caddy placement task and reloading Caddy (`caddy reload --config /etc/caddy/Caddyfile`).
`deploy.yml` doesn't place the Caddyfile, and `caddy_start.yml` only starts Caddy.

#### `src/config/settings/prod.py` — modify

Add the two repo hostnames to `ALLOWED_HOSTS`.

#### Server `.env` files — modify (by hand)

Set `REPO_BASE_URL` and `HCI_BASE_URL` (with `https://`) on each server, then restart
Gunicorn.

#### `docs/how-to.md`, `docs/design.md` — modify

Record the second hostname, the environment variables, and how to reload Caddy. Update
the UptimeRobot note in `docs/design.md` and add a monitor for the repo URL.

## Sources

- https://github.com/ClinGen/hla-curation-interface/issues/87 (issue, the MONDO/CAR
  comment, and the maintainer's comment about `hlarepo.clinicalgenome.org`)
- Notes: "Show evidence summary, other important info in the repo (MONDO links, CAR
  links, etc.)" (content; planned in the `docs/plans/001-ep-review.md` follow-up)
