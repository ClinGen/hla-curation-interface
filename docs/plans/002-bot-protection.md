# Bot Protection

## The Problem

The HCI is a small, specialized tool used by a small number of authorized curators, but
it is publicly reachable on the internet and receives a steady stream of automated
traffic from bots and vulnerability scanners probing for common attack surfaces: exposed
`.env` files, WordPress admin panels, PHP configuration endpoints, and similar targets
that have nothing to do with the application. This traffic is pure noise — none of it
will ever produce a legitimate request — but it consumes server resources, pollutes
logs, and creates unnecessary exposure. The goal is to eliminate this noise at the
network edge before it reaches Django, without introducing meaningful operational
complexity or long-term vendor lock-in.

## The Technical Plan

Every request to the HCI already passes through Caddy, the reverse proxy that sits in
front of the application and handles HTTPS. That makes Caddy the natural first line of
defense: we can configure it to recognize requests for paths that no legitimate user
would ever visit and return an immediate rejection, before the request travels any
further. This is fast, free, and requires no new infrastructure.

Caddy alone, however, only handles individual requests — it has no memory of whether the
same IP address has been probing the server repeatedly. That is where fail2ban comes in.
fail2ban is a small daemon that watches Caddy's access logs in real time. When it sees
the same IP address accumulate too many rejections in a short window, it instructs the
server's firewall to block that address entirely for a period of time. Together, Caddy
and fail2ban cover the two layers of the problem: bad paths are rejected immediately,
and persistent offenders are cut off at the network level.

## Alternatives

**AWS WAF.** AWS offers a managed web application firewall that can be placed in front
of a Lightsail instance via CloudFront or a Network Load Balancer. It would address the
same problem, but it adds meaningful monthly cost (~$5–10/mo at minimum) and ties the
protection layer to AWS — if the server were ever moved to a different host, the WAF
would have to be rebuilt from scratch. Caddy path-blocking and fail2ban achieve the same
outcome with no cost and no lock-in.

**Caddy rate limiting.** Caddy has a third-party rate-limiting plugin
(`caddy-ratelimit`) that could throttle requests per IP directly in the reverse proxy.
The problem is that it is not included in the standard Caddy distribution — using it
requires building a custom Caddy binary with `xcaddy`, which adds meaningful complexity
to both the initial setup and future upgrades. fail2ban achieves the same outcome
(cutting off repeat offenders) using the standard Caddy package and a well-understood,
widely-deployed tool.

## Detailed Implementation

The implementation is organized into three phases matching the technical plan. All
infrastructure changes live in `infra/ansible/`; the existing conventions are followed
throughout (install tasks in `tasks/install/`, config-file placement tasks in
`tasks/placement/`, service-lifecycle tasks in `tasks/admin/`).

### Phase 1: Caddy path-blocking and JSON logging

**`infra/ansible/tasks/placement/files/templates/Caddyfile`** _(modify)_

The only Caddyfile in the project. Currently, it contains two lines: the site block
header and the `reverse_proxy` directive. Three changes are needed:

1. Add a `log` block directing Caddy to write access logs in JSON format to
   `/var/log/caddy/access.log`. JSON logging is required by fail2ban in Phase 2; the
   default plaintext format cannot be reliably parsed by the filter regex.
2. Add a `@blocked` named matcher listing every path prefix that a legitimate user would
   never request (`.env`, `.git`, `wp-admin`, `phpinfo.php`, etc.).
3. Add a `respond @blocked 403` directive that immediately returns a 403 for any request
   matching that list, before it reaches Gunicorn or Django.

No other Ansible files need to change for Phase 1. The existing `placement/caddy.yml`
task already places the Caddyfile, and the existing `admin/caddy_start.yml` task starts
Caddy. After the Caddyfile is updated, a reload (not a full restart) is sufficient to
apply the changes on a running server.

### Phase 2: fail2ban

Six new files and one modification to `init.yml`.

**`infra/ansible/tasks/install/fail2ban.yml`** _(create)_

An Ansible task file that installs the `fail2ban` apt package, following the same
pattern as `tasks/install/caddy.yml`. fail2ban is available in the standard Ubuntu 24.04
package repositories, so no additional GPG key or apt source is needed.

**`infra/ansible/tasks/placement/files/filter.d/caddy-blocked.conf`** _(create)_

The fail2ban filter definition. This file will be copied to
`/etc/fail2ban/filter.d/caddy-blocked.conf` on the server. It contains a `failregex`
that matches lines in Caddy's JSON access log where the `client_ip` field matches the
fail2ban `<HOST>` placeholder and the `status` field is 403 or 404. This is
intentionally broad — it catches any repeated probe, not just the specifically blocked
paths.

**`infra/ansible/tasks/placement/files/jail.d/caddy.conf`** _(create)_

The fail2ban jail configuration. This file will be copied to
`/etc/fail2ban/jail.d/caddy.conf` on the server. It references the filter above, points
`logpath` at `/var/log/caddy/access.log`, and sets the ban parameters: 5 matching
requests within 60 seconds triggers a 24-hour IP ban. These thresholds are a starting
point and can be tightened once real traffic patterns are visible.

**`infra/ansible/tasks/placement/fail2ban.yml`** _(create)_

An Ansible task file that copies the two config files above to their destinations on the
server using `ansible.builtin.copy` with `become: true`. This follows the same pattern
as `tasks/placement/caddy.yml` and `tasks/placement/gunicorn.yml`. The filter goes to
`/etc/fail2ban/filter.d/` and the jail config goes to `/etc/fail2ban/jail.d/`.

**`infra/ansible/tasks/admin/fail2ban_start.yml`** _(create)_

An Ansible task file that enables and starts the `fail2ban` systemd service, following
the same pattern as `tasks/admin/caddy_start.yml` and `tasks/admin/gunicorn_start.yml`.

**`infra/ansible/playbooks/init.yml`** _(modify)_

The server initialization playbook. Three new task includes need to be added after the
Caddy placement and start tasks, in order: install fail2ban, place the fail2ban config
files, and start fail2ban. The ordering matters — fail2ban must be installed before its
config files are placed, and config files must be in place before the service starts.
fail2ban does not need to be added to `deploy.yml` because its config does not change on
a normal code deploy.
