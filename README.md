# HubSign Landing Page

Marketing site for HubSign, built with Django 4.2 and server-rendered templates.
No Node, no bundler, no JS framework — hand-written CSS and vanilla JS.

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit http://localhost:8000.

Docker: `docker-compose up` for development; see [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for production.

## Routes

| Path | What |
|---|---|
| `/` | The entire landing page (single page, anchored sections) |
| `/legal/privacy/` | Privacy Policy — PIPEDA / Quebec Law 25 / GDPR |
| `/legal/terms/` | Website Terms of Use |
| `/legal/cookies/` | Cookie Policy |
| `/legal/refunds/` | Cancellation & Refunds |
| `/legal/accessibility/` | Accessibility Statement |
| `/pricing/` | Redirects to `/#pricing` |
| `/api/pricing/` | Pricing tiers as JSON |
| `/api/health/` | Health check (used by Docker, compose and nginx) |
| `/robots.txt`, `/sitemap.xml` | |
| `/admin/` | Django admin |

`/api/schema/` and `/api/docs/` (Swagger) exist but are **off unless `EXPOSE_API_DOCS=true`** —
they enumerate the API surface and are of no use on a marketing site.

## Layout

```
hubsign/          Django project — settings, urls, wsgi, security-header middleware
landing/          The site: views, pricing, legal pages, company details, checks
api/              Two read-only JSON endpoints (pricing, health)
templates/        base.html, landing/index.html, legal/*, components/icons/*
static/           css/main.css, js/main.js, fonts/*.woff2, images/*
nginx/            Production reverse proxy
```

## Three things that are easy to break

**1. The site sets no cookies, and that is load-bearing.**
No analytics, no third-party embeds, fonts self-hosted. That is *why* there is no cookie
consent banner and why `/legal/cookies/` says what it says. Adding a tracker, an embed, or
anything that reads `csrf_token` in a template means you also need a consent mechanism and a
rewrite of that page. `landing/tests_legal.py` fails if a cookie appears.

**2. Business details live in `landing/company.py`.**
Anything not yet confirmed is an `Unknown`, which renders as a loud `[[NEEDS CONFIRMATION]]`
marker and is reported by `manage.py check` (`landing.W001`). Fill in the real values there —
never inline in a template. See [LEGAL_REVIEW.md](LEGAL_REVIEW.md) for what is outstanding.

**3. Pricing has one source of truth: `landing/pricing.py`.**
Both the server-rendered page and `/api/pricing/` read it. See `PRODUCTION_INCIDENT.md` for
what happened when there were two copies. The "Save up to N%" badge is *derived* from the real
prices (`max_annual_saving_percent`) — do not hardcode it; Business and Enterprise Shared save
17%, not 20%.

## Design

Editorial layout on a warm paper ground, with the product pipeline drawn once as the hero
"spine" and reused elsewhere only as a small six-dot position marker.

Three typefaces, one job each — **Fraunces** (headings), **Inter** (body, UI, tabular figures),
**IBM Plex Mono** (system labels only). All self-hosted from `static/fonts/`, all SIL OFL 1.1
with licences shipped alongside.

Colour tokens are at the top of `static/css/main.css`. Every text/background pair used is
asserted at WCAG AA by `landing/tests_a11y.py::PaletteContrastTests` — add new pairings there.

`static/images/og-image.png` (the Open Graph / Twitter card image) is generated, not hand-made — re-run `node tools/generate_og_image.mjs` after changing the headline, wordmark, or hero screenshot (needs the Playwright Chromium install from the sibling `hubsign_by_documenso` repo).

## Accessibility

Targets WCAG 2.1 AA plus the WCAG 2.2 target-size criterion. State changes must update ARIA,
not just a CSS class; there are no inline event handlers (that is what lets the CSP forbid
inline script).

```bash
python manage.py test                  # includes contrast, ARIA and cookie-posture tests

# Optional browser pass — needs `pip install playwright && playwright install chromium`
python tools/browser_audit.py          # axe-core, keyboard, reflow, against a running server
```

## Environment

```env
SECRET_KEY=...                 # required in production
DEBUG=False
ALLOWED_HOSTS=hubsign.io,www.hubsign.io
CSRF_TRUSTED_ORIGINS=https://hubsign.io
EXPOSE_API_DOCS=false          # Swagger UI, off by default
NEXT_PUBLIC_FEATURE_BILLING_ENABLED=false
NEXT_PRIVATE_STRIPE_API_KEY=
```

Run `python manage.py check --deploy` before shipping.

## Deploying

Production runs through Komodo, not `docker-compose.prod.yml`. **A redeploy without a rebuild
serves stale CSS, JS and fonts** — trigger a Build, then Deploy, then purge the Cloudflare
cache. `PRODUCTION_INCIDENT.md` has the full detail.

## Support

- Sales: sales@hubsign.io
- Support: support@hubsign.io
- Docs: https://docs.hubsign.io

© 2026 Future Edge Technology Inc.
