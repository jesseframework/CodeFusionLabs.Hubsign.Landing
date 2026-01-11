# HubSign Landing - Django Setup Guide

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your SECRET_KEY

# 4. Run migrations
python manage.py migrate

# 5. Collect static files (for production)
python manage.py collectstatic --noinput

# 6. Run development server
python manage.py runserver
```

Visit http://localhost:8000

## Project Structure

```
hubsign/
├── hubsign/              # Django project settings
│   ├── settings.py       # Configuration
│   ├── urls.py           # Root URL routing
│   └── wsgi.py           # WSGI entry point
├── landing/              # Landing page app
│   ├── views.py          # Page views
│   ├── urls.py           # Landing routes
│   └── templates/        # Django templates
├── api/                  # REST API app
│   ├── views.py          # API endpoints
│   ├── urls.py           # API routes
│   └── serializers.py    # DRF serializers
├── static/               # Static files (CSS, JS, images)
├── templates/            # Shared templates
└── manage.py
```

## Key Features

### Sign-In Flow
The modal supports two paths:
1. **Company Instance** - User enters subdomain → validates via API → redirects to `{subdomain}.hubsign.io`
2. **Shared Instance** - User enters email → sends magic link → shows success message

### API Endpoints
- `/api/v1/tenant/validate/` - POST - Validate subdomain exists
- `/api/v1/auth/magic-link/` - POST - Send passwordless login email
- `/api/v1/health/` - GET - Health check

## Next Steps

1. Update `.env` with your actual settings
2. Add logo files to `static/images/` (hubsign_logo.png, fepro_logo.png)
3. Configure email backend in settings.py for magic links
4. Set up production deployment (see Django deployment docs)
