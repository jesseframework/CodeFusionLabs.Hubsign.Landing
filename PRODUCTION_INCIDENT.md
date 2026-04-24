# Production Incident: Static Images 404 + Stripe Pricing Mismatch

**Date:** April 2026  
**Status:** Resolved  

---

## What Went Wrong

### 1. Images 404 in Production

Static images (`hubsign_logo.png`, `fepro_logo.png`, favicons) were returning 404 for all visitors despite the files existing in the git repository.

**Root cause chain:**

1. **Komodo uses a private Docker registry** at `172.16.15.51:5000`, not GitHub Actions or a local build on deploy. The image tag is `172.16.15.51:5000/futureedge/hubsign-landing:latest`.

2. **The image in the registry was stale** — built before `static/images/` was committed to git. The images were added in commit `fe4d366` but the registry image predated it. Every deploy just re-ran this old image.

3. **The Komodo `compose.yaml` runs `collectstatic` at container startup** (not a Dockerfile issue). Because the source files (`/app/static/images/`) didn't exist in the stale image, collectstatic had nothing to collect. It reported `0 static files copied, 156 unmodified` — the 156 are the stale CSS/JS that were baked in from an older build.

4. **`collectstatic` ran without `--clear`** so stale files in the staticfiles directory were never removed, and new files were only added if they didn't already exist.

5. **Cloudflare cached the 404 response** (`Cache-Control: max-age=14400`) so even fixing the origin temporarily required a manual Cloudflare cache purge to see the result.

6. The `STATICFILES_STORAGE` was set to `CompressedManifestStaticFilesStorage`, which has `manifest_strict = False` internally (WhiteNoise's version). When a file is missing from the manifest, it silently returns the plain URL. WhiteNoise then can't find the plain file either (only hashed versions exist), resulting in a `text/html` 404 instead of a binary image response — making the problem hard to diagnose.

---

### 2. Stripe Pricing Tier ID Mismatch

The `/api/pricing/` endpoint was not returning live Stripe data even though `BILLING_ENABLED=true` and `STRIPE_API_KEY` were set.

**Root cause:** The code expected Stripe products with `metadata.plan` values of `community`, `team`, `regular`, `platform`, `enterprise`. The actual Stripe products had `metadata.plan` set to `personal`, `individual`, `business`, `enterprise`. No products matched → fell back to hardcoded values.

Additionally, the initial prices shown on page load came from the Django view context (hardcoded fallback in `landing/views.py`), not from Stripe. Stripe prices were only applied after the user clicked the monthly/annual toggle.

---

### 3. Komodo `compose.yaml` Runtime Workarounds

The Komodo compose file had accumulated several shell workarounds that patched the running container instead of fixing root causes in code:

```sh
pip install requests   # requests wasn't in requirements.txt
sed -i "s/SECURE_SSL_REDIRECT = True/SECURE_SSL_REDIRECT = False/g" ...   # redirect loop workaround
sed -i "s/ManifestStaticFilesStorage/StaticFilesStorage/g" ...   # manifest 404 workaround
python manage.py collectstatic --noinput   # missing --clear
```

These hid real bugs and made behaviour dependent on fragile string-matching at runtime.

---

### 4. GitHub Actions CI Broken

The `.github/workflows/docker-build.yml` used `cache-to: type=gha,mode=max` without first setting up Docker Buildx. The default Docker driver doesn't support GHA cache export, so every CI run failed with:

```
ERROR: Cache export is not supported for the docker driver. Switch to a different driver
```

This didn't block Komodo (Komodo builds independently via its own build step), but it meant GitHub Container Registry (`ghcr.io`) never received a fresh image push.

---

## The Fix

### In Komodo UI (`compose.yaml`)

Removed all runtime workarounds. Cleaned command to:

```yaml
command:
  - /bin/sh
  - -c
  - |
    python manage.py collectstatic --noinput --clear
    exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 60 hubsign.wsgi:application
```

Key changes:
- Removed `pip install requests`
- Removed both `sed` patches
- Added `--clear` to collectstatic

### In Code (merged to `main`)

| File | Change | Why |
|------|--------|-----|
| `hubsign/settings.py` | `STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'` | Avoids manifest complexity. Files served at plain original URLs. No silent fallback behaviour. |
| `hubsign/settings.py` | `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` in `if not DEBUG` block | Trusts nginx's `X-Forwarded-Proto` header so `SECURE_SSL_REDIRECT` doesn't loop behind the reverse proxy. |
| `Dockerfile` | Added `test -f /app/static/images/hubsign_logo.png` guards before collectstatic | Build fails immediately if images are missing from the build context instead of silently deploying a broken image. |
| `Dockerfile` | `ENV DEBUG=False SECRET_KEY=... DJANGO_SETTINGS_MODULE=hubsign.settings` before collectstatic | Ensures collectstatic always runs in production mode regardless of host environment variables. |
| `Dockerfile` | `collectstatic --noinput --clear --verbosity 2` | `--clear` removes stale files. `--verbosity 2` outputs every file collected — visible in Komodo build logs. |
| `Dockerfile` | Removed `apt-get install gcc postgresql-client` | Not needed. App uses SQLite and all Python packages are pure Python. Slowed down builds unnecessarily. |
| `Dockerfile` | Fixed `HEALTHCHECK` to use `urllib.request` and `/api/health/` | Was using `import requests` (not guaranteed installed) and wrong URL `/api/v1/health/`. |
| `api/views.py` | `_TIER_ORDER = ['personal', 'individual', 'business', 'enterprise']` | Matches actual Stripe product `metadata.plan` values. |
| `api/views.py` | Updated fallback tier prices to match Stripe | `business: $60/$50`, `enterprise: $200/$180`. |
| `landing/views.py` | Updated tier IDs and prices to match Stripe | Server-rendered initial prices now match what Stripe returns so the JS `data-tier` lookup works on page load. |
| `static/js/main.js` | Call `applyPricingTiers()` immediately after `/api/pricing/` resolves | Stripe prices now shown on page load, not only after clicking the toggle. |
| `.github/workflows/docker-build.yml` | Added `docker/setup-buildx-action@v3` step | Required for `cache-to: type=gha` to work. Fixes CI. |

### Deployment Sequence That Fixed It

1. Merge code changes to `main`
2. In Komodo: trigger a **BUILD** (not just deploy) — this rebuilds the Docker image from the latest git code and pushes to `172.16.15.51:5000/futureedge/hubsign-landing:latest`
3. Redeploy the stack
4. Purge Cloudflare cache (Caching → Purge Everything)

---

## Notes for Future Builds and Updates

### Deployment Model

```
git push → main
    ↓
Komodo BUILD (pulls latest main, builds Docker image, pushes to 172.16.15.51:5000)
    ↓
Komodo DEPLOY (docker stack deploy -c compose.yaml)
    ↓
Container starts → collectstatic --clear → gunicorn
```

**Redeploy alone is not enough after code changes.** You must trigger a **Build** first, then Deploy.

### When Images or Static Files Break

1. Check Komodo build logs for the collectstatic output. Look for:
   - `test -f` guard failure: `ERROR: hubsign_logo.png not found in build context` → images missing from git or excluded by `.dockerignore`
   - `Copying 'images/hubsign_logo.png'` lines (verbosity 2 output) → confirms files are being collected
2. Check `cf-cache-status` in browser DevTools. If `HIT`, purge Cloudflare cache first before concluding origin is broken.
3. The image URL in the HTML should be plain (e.g. `/static/images/hubsign_logo.png`) — if you see a hashed URL, the storage backend has changed back to a manifest-based one.

### Architecture: Two Django Projects in the Repo

The repo has TWO Django project structures:
- **ROOT** (`/app/`) — what Docker builds and runs
- **`hubsign/` subdirectory** — inner project, NOT used in production

Docker runs gunicorn with `hubsign.wsgi:application` from WORKDIR `/app`. This resolves to `/app/hubsign/wsgi.py` (outer), which uses settings at `/app/hubsign/settings.py`. The `landing` and `api` apps are the ROOT-level ones at `/app/landing/` and `/app/api/`. Templates are at `/app/templates/`. Static source files are at `/app/static/`.

**Never edit files inside `hubsign/landing/`, `hubsign/api/`, `hubsign/static/`, or `hubsign/templates/` — those are the inner project and are not deployed.**

### Stripe Pricing

The `/api/pricing/` endpoint fetches live prices from Stripe when:
- `NEXT_PUBLIC_FEATURE_BILLING_ENABLED=true` in Komodo environment
- `NEXT_PRIVATE_STRIPE_API_KEY=sk_live_...` in Komodo environment

Stripe products must have a `metadata.plan` field set to one of:  
`personal` | `individual` | `business` | `enterprise`

If no products match, the endpoint silently falls back to hardcoded prices. To verify Stripe data is flowing: hit `https://hubsign.io/api/pricing/` — if `price_id_monthly` fields are non-null, Stripe is working.

### Komodo `compose.yaml` vs `docker-compose.prod.yml`

Komodo uses `compose.yaml` (configured in the Komodo UI), **not** `docker-compose.prod.yml` from the git repo. These are separate files. Changes to `docker-compose.prod.yml` in git do not affect what Komodo runs. Environment variables, volumes, commands, and resource constraints are all set in the Komodo UI.

### Cloudflare Caching

Static 4xx responses are cached by Cloudflare with `max-age=14400` (4 hours). After any deploy that fixes a previously 404 URL, purge the Cloudflare cache:  
**Cloudflare Dashboard → hubsign.io → Caching → Purge Cache → Purge Everything**

### Security Notes

- `ALLOWED_HOSTS=*` is currently set in the Komodo compose environment. This should be restricted to `hubsign.io,www.hubsign.io` when possible.
- `DEBUG=false` is set in compose. Confirm this is lowercase `false` — Django reads it via `os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')`, so both `false` and `False` evaluate to `False` correctly.
- `SECURE_SSL_REDIRECT` is controlled by the `if not DEBUG:` block in settings. With `DEBUG=False` it will be `True`, but `SECURE_PROXY_SSL_HEADER` is now set so nginx's `X-Forwarded-Proto: https` prevents redirect loops.
