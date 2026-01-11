# HubSign Landing Page

Enterprise e-signature SaaS landing page built with Django, Docker-ready for production.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Development
docker-compose up

# Production
cp .env.production.example .env.production
# Edit .env.production with your settings
./deploy.sh
```

### Option 2: Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
python manage.py migrate
python manage.py runserver
```

Visit: **http://localhost:8000**

## 📚 Documentation

- **[Docker Guide](DOCKER_GUIDE.md)** - Complete Docker deployment guide
- **[Setup Guide](SETUP.md)** - Local development setup
- **[Conversion Guide](CONVERSION_COMPLETE.md)** - Django architecture details
- **[Font Guide](FONTS_GUIDE.md)** - Typography and font options

## 🏗️ Tech Stack

- **Framework:** Django 4.2
- **API:** Django REST Framework
- **Database:** PostgreSQL (production) / SQLite (development)
- **Server:** Gunicorn + Nginx
- **Deployment:** Docker + Docker Compose
- **SSL:** Let's Encrypt (Certbot)
- **Fonts:** Inter + Plus Jakarta Sans

## 🎯 Features

- ✅ Responsive single-page design
- ✅ Dual sign-in flow (subdomain + magic link)
- ✅ REST API endpoints
- ✅ CSRF & CORS protection
- ✅ Docker production-ready
- ✅ SSL/TLS support
- ✅ Health checks & monitoring
- ✅ Rate limiting
- ✅ Static file optimization

## 📦 Project Structure

```
hubsign/                 # Django project settings
├── settings.py         # Configuration
├── urls.py            # Root routing
└── wsgi.py            # WSGI entry

landing/                # Landing page app
├── templates/         # Django templates
├── views.py          # Page views
└── urls.py           # Landing routes

api/                    # REST API
├── views.py          # API endpoints
├── urls.py           # API routes
└── serializers.py    # Data serializers

static/
├── css/main.css      # Styles
├── js/main.js        # JavaScript
└── images/           # Assets

nginx/
└── nginx.conf        # Production reverse proxy

docker-compose.yml      # Development stack
docker-compose.prod.yml # Production stack
Dockerfile             # Application image
```

## 🔧 Environment Variables

Create `.env` file:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🚢 Deployment

### Quick Deploy

```bash
./deploy.sh
```

### Manual Deploy

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Setup SSL
./setup-ssl.sh your-domain.com your-email@domain.com
```

See **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** for complete deployment instructions.

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/tenant/validate/` | POST | Validate subdomain |
| `/api/v1/auth/magic-link/` | POST | Send login email |
| `/api/v1/auth/signup/` | POST | Create account |
| `/api/v1/health/` | GET | Health check |

## 🔒 Security

- CSRF protection
- CORS configuration
- SSL/TLS encryption
- Security headers
- Rate limiting
- Non-root containers
- Environment secrets

## 📝 License

© 2026 Future Edge Technology Inc. All rights reserved.

## 🤝 Support

- **Email:** support@hubsign.io
- **Website:** https://hubsign.io
