# HubSign Landing Page — working notes

Django 4.2, server-rendered. **No Node, no bundler, no JS framework.** Hand-written CSS in
`static/css/main.css` and vanilla JS in `static/js/main.js`.

> This file was substantially rewritten in September 2026. It previously described an inner
> `hubsign/landing/` project, a sign-in modal, `/api/v1/` endpoints and Fraunces/DM Sans
> typography — none of which existed any more. If something here disagrees with the code,
> trust the code and fix this file.

## Layout

```
hubsign/          settings.py, urls.py, wsgi.py, middleware.py  (the Django project)
landing/          views.py, pricing.py, legal.py, company.py, checks.py, sitemap.py
api/              views.py, urls.py  — two read-only JSON endpoints
templates/        base.html, landing/index.html, legal/*.html, components/icons/*.svg
static/           css/main.css, js/main.js, fonts/*.woff2, images/*
tools/            browser_audit.py  (optional Playwright pass)
```

There used to be a second, undeployed Django project nested under `hubsign/`. It has been
deleted. If you find references to `hubsign/landing/` or `hubsign/static/`, they are stale.

## Four rules that are easy to break

**1. No cookies. No third parties.**
The site sets no cookies, loads no analytics, and self-hosts its fonts. That is why there is no
consent banner and why `/legal/cookies/` reads as it does. Anything that adds a tracker, an
embed, or a template that reads `csrf_token` breaks that promise — and
`landing/tests_legal.py` will fail. If you genuinely need one, add a real consent mechanism and
rewrite the cookie policy first.

**2. State changes must update ARIA, not just a class.**
`aria-expanded`, `aria-selected`, `aria-current`, `hidden`. A CSS class alone is invisible to
assistive technology. And **no inline event handlers** — every listener is bound in `main.js`,
which is what lets the CSP forbid inline script. `landing/tests_a11y.py` enforces both.

**3. Colours come from the tokens in `:root`, and new pairings get a test.**
`landing/tests_a11y.py::PaletteContrastTests` asserts every text/background pair at WCAG AA
(3:1 for meaningful graphics). Add your pairing to that list. The palette this replaced had
five failures in production.

**4. Business details live in `landing/company.py`.**
Never inline a company address, phone number or officer name in a template. Unconfirmed values
are `Unknown` instances that render a visible `[[NEEDS CONFIRMATION]]` marker and trip the
`landing.W001` system check. See `LEGAL_REVIEW.md`.

## Design system

Editorial layout, warm paper ground (`--paper`), deep navy ink, purple as an accent rather than
a wash. Hairline rules instead of boxes-in-boxes.

Four typefaces, one job each — never mix them up:

| Token | Family | Used for |
|---|---|---|
| `--font-display` | Fraunces | `h1`–`h3` only. Shipped as `fraunces-wonk.woff2`: SOFT=50 and WONK=1 are baked in (only weight and optical size stay variable) |
| `--font-body` | Inter | body, UI, tabular figures |
| `--font-mono` | IBM Plex Mono | small system labels only — field types, code-ish chips |
| `--font-hand` | Caveat | the "pen" marks only — margin notes, stamps, the Commodity tag. Never body text or headings |

All self-hosted from `static/fonts/`, all SIL OFL 1.1 with licences shipped. Do not add a
Google Fonts `<link>`.

**The spine** is the page's one diagram: the six-step pipeline from `PIPELINE` in
`landing/views.py`, drawn full size once in the hero as a real `<ol>`. Elsewhere it appears only
as a decorative six-dot marker (`.spine-mini`, `aria-hidden`) beside a text label. Keep it that
way — repeating the full diagram is what would make the page feel crowded.

Spacing uses the `--space-1`…`--space-9` scale. Breakpoints: **1000px**, **860px**, **620px**.

## Templates

- `{% load static %}`, `{% static 'css/main.css' %}`, `{% extends "base.html" %}`
- Icons: `{% include "components/icons/check.svg" %}`, or built dynamically with
  `{% include "components/icons/"|add:pillar.icon|add:".svg" %}`. Every icon carries
  `aria-hidden="true"`; only add one that a text label accompanies.
- Legal pages extend `templates/legal/_base.html` and fill `{% block toc %}` and
  `{% block body %}`.
- Decorative mockups use the `.mock-*` classes and must sit inside an `aria-hidden="true"`
  container.

## Pricing

`landing/pricing.py` is the single source of truth, shared by the page and `/api/pricing/`
(see `PRODUCTION_INCIDENT.md` for what two copies cost). Both monthly and annual figures are
server-rendered into `data-monthly` / `data-annual`, so the billing toggle needs no network.

The savings badge is derived by `max_annual_saving_percent()` — **do not hardcode a percentage.**
Business and Enterprise Shared save 17%, not 20%.

## Landing page sections

`#top` hero + spine · stats · `#product` · `#signing` · `#showcase` (9-panel carousel) ·
`#integrations` · `#pricing` · `#faq` · final CTA.

## Testing

```bash
python manage.py test          # markup, ARIA, contrast tokens, cookies, headers, claims
python manage.py check --deploy
python tools/browser_audit.py  # optional: axe-core, keyboard, reflow (needs playwright)
```

## Deploying

Production runs through Komodo. **A redeploy without a rebuild serves stale CSS, JS and fonts.**
Build → Deploy → purge Cloudflare. Details in `PRODUCTION_INCIDENT.md`.
