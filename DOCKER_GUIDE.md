# 🐳 Docker Deployment Guide

Your HubSign Landing application is now Docker-ready for production deployment!

## 📋 What's Been Added

### Core Docker Files
- ✅ `Dockerfile` - Production-ready Python/Django image
- ✅ `docker-compose.yml` - Development environment
- ✅ `docker-compose.prod.yml` - Production environment with SSL
- ✅ `.dockerignore` - Optimized build context
- ✅ `nginx/nginx.conf` - Production reverse proxy with SSL
- ✅ `.env.production.example` - Production environment template

### Helper Scripts
- ✅ `build-docker.sh` - Build Docker images
- ✅ `deploy.sh` - One-command production deployment

---

## 🚀 Quick Start

### Development (Local Docker)

```bash
# 1. Start all services
docker-compose up

# 2. Access the app
open http://localhost:8000

# 3. View logs
docker-compose logs -f

# 4. Stop services
docker-compose down
```

### Production Deployment

```bash
# 1. Configure environment
cp .env.production.example .env.production
# Edit .env.production with your settings

# 2. Deploy
chmod +x deploy.sh
./deploy.sh

# 3. Setup SSL (first time only)
./setup-ssl.sh your-domain.com your-email@domain.com
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Nginx (Port 80/443)            │
│         SSL Termination + Static Files       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         Django/Gunicorn (Port 8000)         │
│            Python Web Application            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          PostgreSQL (Port 5432)             │
│              Database Server                 │
└─────────────────────────────────────────────┘
```

---

## 📦 Docker Services

### 1. **web** - Django Application
- **Image:** Custom (built from Dockerfile)
- **Ports:** 8000
- **Features:**
  - Gunicorn WSGI server (4 workers)
  - Health checks every 30s
  - Auto-restart on failure
  - Non-root user for security

### 2. **db** - PostgreSQL Database
- **Image:** postgres:15-alpine
- **Ports:** 5432 (internal only)
- **Features:**
  - Persistent volume storage
  - Health checks
  - Auto-restart

### 3. **nginx** - Reverse Proxy
- **Image:** nginx:alpine
- **Ports:** 80, 443
- **Features:**
  - SSL/TLS termination
  - Static file serving
  - Gzip compression
  - Rate limiting
  - Security headers

### 4. **certbot** - SSL Certificates
- **Image:** certbot/certbot
- **Features:**
  - Auto SSL renewal
  - Let's Encrypt integration

---

## 🔧 Configuration

### Environment Variables (.env.production)

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=hubsign.io,www.hubsign.io

# Database
DB_NAME=hubsign_prod
DB_USER=hubsign_user
DB_PASSWORD=super-secure-password
DB_HOST=db
DB_PORT=5432

# Email (for magic links)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@hubsign.io
EMAIL_HOST_PASSWORD=your-email-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 📝 Common Commands

### Development

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild images
docker-compose up --build

# View logs
docker-compose logs -f web
docker-compose logs -f db

# Execute commands in container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Production

```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Restart service
docker-compose -f docker-compose.prod.yml restart web

# Stop everything
docker-compose -f docker-compose.prod.yml down
```

---

## 🔒 SSL Setup (Let's Encrypt)

### Initial SSL Setup

1. **Update nginx.conf** with your domain
2. **Run certbot:**

```bash
# Request certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  -d hubsign.io -d www.hubsign.io \
  --email your-email@domain.com \
  --agree-tos --no-eff-email

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Auto-Renewal

Certificates auto-renew every 12 hours via the certbot service.

---

## 🚢 Publishing to Container Registry

### Docker Hub

```bash
# Login
docker login

# Tag image
docker tag hubsign-landing:latest yourusername/hubsign-landing:latest
docker tag hubsign-landing:latest yourusername/hubsign-landing:v1.0.0

# Push
docker push yourusername/hubsign-landing:latest
docker push yourusername/hubsign-landing:v1.0.0
```

### GitHub Container Registry

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag
docker tag hubsign-landing:latest ghcr.io/jesseframework/hubsign-landing:latest

# Push
docker push ghcr.io/jesseframework/hubsign-landing:latest
```

### AWS ECR

```bash
# Login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag
docker tag hubsign-landing:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/hubsign-landing:latest

# Push
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/hubsign-landing:latest
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8000/api/v1/health/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-11T12:00:00Z"
}
```

### Container Health

```bash
# Check container health
docker-compose ps

# View health logs
docker inspect hubsign-web | grep -A 10 Health
```

---

## 🔍 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs web

# Check specific error
docker-compose logs web | grep ERROR
```

### Database connection issues

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec web python manage.py dbshell
```

### Static files not loading

```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx config
docker-compose exec nginx nginx -t
```

### SSL certificate issues

```bash
# Check certificate
docker-compose exec nginx ls -la /etc/letsencrypt/live/

# Renew manually
docker-compose run --rm certbot renew
```

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Set `DJANGO_DEBUG=False` in .env.production
- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set secure database password
- [ ] Configure email backend
- [ ] Setup SSL certificates
- [ ] Configure domain DNS to point to server
- [ ] Test health endpoint
- [ ] Setup monitoring/logging
- [ ] Configure backups for database
- [ ] Review security headers in nginx.conf

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.prod.yml
services:
  web:
    deploy:
      replicas: 3  # Run 3 instances
```

### Vertical Scaling

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## 🔐 Security Features

- ✅ Non-root user in container
- ✅ SSL/TLS encryption
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Rate limiting
- ✅ CSRF protection
- ✅ Secure cookies
- ✅ Environment variable secrets
- ✅ Database connection encryption

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**🎉 Your application is Docker-ready!**

Run `./deploy.sh` when you're ready to deploy to production!
