# HubSign Landing Page - Django Application

## Project Overview

This is a **Django-based landing website** for HubSign, an enterprise e-signature SaaS product. Converted from a static HTML page to a full Python web application with API support.

## Project Structure

```
hubsign/
├── hubsign/              # Django project settings
│   ├── settings.py       # Configuration (security, apps, middleware)
│   ├── urls.py           # Root URL routing
│   └── wsgi.py           # WSGI entry point
├── landing/              # Landing page app
│   ├── templates/landing/
│   │   ├── base.html     # Base template with CSS/JS
│   │   ├── index.html    # Main landing page
│   │   ├── components/   # Reusable template partials
│   │   └── icons/        # SVG icon templates
│   ├── views.py          # Page views
│   └── urls.py           # Landing URL routes
├── api/                  # REST API app
│   ├── views.py          # API endpoints
│   ├── urls.py           # API routes (/api/v1/...)
│   └── serializers.py    # DRF serializers
├── static/
│   ├── css/main.css      # All CSS styles
│   ├── js/main.js        # All JavaScript
│   └── images/           # Logo files
└── manage.py
```

## Key Commands

```bash
# Setup
cd hubsign
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Development
python manage.py runserver           # Start dev server at localhost:8000
python manage.py migrate             # Run database migrations
python manage.py collectstatic       # Collect static files for production

# Testing
python manage.py test                # Run all tests
python manage.py test landing        # Run landing app tests
```

## Template Conventions

### Django Template Syntax
- Use `{% load static %}` at top of templates needing static files
- Static files: `{% static 'css/main.css' %}`
- Template inheritance: `{% extends "landing/base.html" %}`
- Include components: `{% include "landing/components/header.html" %}`
- CSRF token in forms: `{% csrf_token %}`

### Component Pattern
Reusable components live in `landing/templates/landing/components/`:
- `header.html` - Navigation header
- `footer.html` - Page footer  
- `modal.html` - Sign-in modal with subdomain/shared instance flow

### Icon System
SVG icons are in `landing/templates/landing/icons/` and included via:
```django
{% include "landing/icons/check.html" %}
```

## CSS Architecture

All styles in `static/css/main.css`. Use CSS variables from `:root`:
- Colors: `--primary`, `--purple-50` to `--purple-900`
- Spacing: `--radius-sm/md/lg/xl`, `--shadow-sm/md/lg/xl`
- Typography: `--font-display` (Fraunces), `--font-body` (DM Sans)
- Transitions: `--transition-fast` (150ms), `--transition-base` (200ms)

### Component Classes
- **Buttons**: `.btn` with `.btn-primary`, `.btn-outline`, `.btn-ghost`, `.btn-lg`, `.btn-sm`, `.btn-full`
- **Sections**: `.section` > `.container` > `.section-header`
- **Cards**: `.feature-card`, `.pricing-card`, `.doc-preview`

## JavaScript Patterns

All JS in `static/js/main.js`:
- Uses CSRF token from cookie for API calls
- Modal state managed via `modalState` object
- Functions exported to `window` for onclick handlers

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/tenant/validate/` | POST | Validate subdomain exists |
| `/api/v1/auth/magic-link/` | POST | Send passwordless login email |
| `/api/v1/auth/signup/` | POST | Create new account |
| `/api/v1/health/` | GET | Health check |

## Sign-In Flow

The modal (`components/modal.html`) supports three paths:
1. **Company Instance** - User enters subdomain → validates via API → redirects to `{subdomain}.hubsign.io`
2. **Shared Instance** - User enters email → sends magic link → shows success message
3. **Signup** - New user registration with email, name, company

## Security

- CSRF protection on all forms
- Security middleware enabled (XSS, content type sniffing, HSTS in prod)
- Environment variables for secrets (see `.env.example`)
- HTTPS enforcement in production

## Adding New Features

1. **New Page**: Add view in `landing/views.py`, route in `landing/urls.py`, template in `templates/landing/`
2. **New API**: Add view in `api/views.py`, route in `api/urls.py`
3. **New Component**: Create in `templates/landing/components/`, include where needed
4. **New Icon**: Add SVG in `templates/landing/icons/`

## Key Sections (Landing Page)

| Section ID | Purpose |
|------------|---------|
| `#features` | 6-card feature grid |
| `#how-it-works` | 3-step process with connectors |
| `#pricing` | 4-tier pricing grid with monthly/annual toggle |
| `#compliance` | Legal compliance badges (ESIGN, UETA, eIDAS) |

## Responsive Breakpoints

```css
@media (max-width: 1024px)  /* Tablet: 2-col grids, center hero */
@media (max-width: 768px)   /* Mobile: 1-col, hide nav, show mobile menu */
@media (max-width: 480px)   /* Small: Stack buttons vertically */
```

## Environment Variables

Create `.env` file:
```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.hubsign.io
```
