"""
Django settings for HubSign Landing project.
"""
import os
from pathlib import Path

from csp.constants import NONE, SELF

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip() 
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    # Local apps
    'landing',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'hubsign.middleware.SecurityHeadersMiddleware',
]

# django-browser-reload is a development-only tool. It used to be installed
# unconditionally, which shipped its middleware and app to production.
if DEBUG:
    INSTALLED_APPS.append('django_browser_reload')
    MIDDLEWARE.insert(
        MIDDLEWARE.index('whitenoise.middleware.WhiteNoiseMiddleware') + 1,
        'django_browser_reload.middleware.BrowserReloadMiddleware',
    )

ROOT_URLCONF = 'hubsign.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'landing.context_processors.company',
            ],
        },
    },
]

WSGI_APPLICATION = 'hubsign.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# CSRF
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS', 
        'http://localhost:8000,http://127.0.0.1:8000'
    ).split(',')
]

# Response security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
# Tighter than nginx's previous 'no-referrer-when-downgrade', which leaked the
# full URL to any same-protocol third party.
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'
# Django has no Permissions-Policy setting; hubsign.middleware adds it.
PERMISSIONS_POLICY = 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()'

# Session security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF cookie
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# Content Security Policy
#
# django-csp 4.x replaced the flat CSP_* settings with this dict. The old
# CSP_DEFAULT_SRC / CSP_SCRIPT_SRC / ... names are silently IGNORED by 4.x, so
# the policy this project thought it had was never actually being sent. Keep
# this in the dict form and keep requirements.txt pinned to >=4,<5.
#
# No third-party origins are allowed: fonts are self-hosted from static/fonts/
# (see templates/base.html) and the site loads no analytics, tag manager, chat
# widget or CDN script. Adding any of those means editing this policy AND
# revisiting the cookie policy at /legal/cookies/.
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': [SELF],
        # No 'unsafe-inline': every handler is bound in static/js/main.js.
        'script-src': [SELF],
        # 'unsafe-inline' is required only for per-element style="" attributes on
        # the CSS mockups (skeleton bar widths in templates/landing/index.html).
        # The page renders no user-supplied content, so this is not an XSS vector.
        'style-src': [SELF, "'unsafe-inline'"],
        'font-src': [SELF],
        'img-src': [SELF, 'data:'],
        'connect-src': [SELF],
        'form-action': [SELF],
        'base-uri': [SELF],
        'frame-ancestors': [NONE],
        'object-src': [NONE],
    },
}

# CORS (for API access)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# HTTPS settings (enable in production)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# =============================================================================
# REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'HubSign API',
    'DESCRIPTION': 'API for HubSign e-signature platform',
    'VERSION': '1.0.0',
}

# =============================================================================
# HUBSIGN CONFIGURATION
# =============================================================================

EXPOSE_API_DOCS = os.environ.get('EXPOSE_API_DOCS', 'False').lower() in ('true', '1', 'yes')

HUBSIGN_API_URL = os.environ.get('HUBSIGN_API_URL', 'https://api.hubsign.io')
HUBSIGN_API_KEY = os.environ.get('HUBSIGN_API_KEY', '')

# =============================================================================
# BILLING / STRIPE CONFIGURATION
# =============================================================================

BILLING_ENABLED = os.environ.get('NEXT_PUBLIC_FEATURE_BILLING_ENABLED', 'false').lower() in ('true', '1', 'yes')
STRIPE_API_KEY = os.environ.get('NEXT_PRIVATE_STRIPE_API_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('NEXT_PRIVATE_STRIPE_WEBHOOK_SECRET', '')
