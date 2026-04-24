# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Create static files directory
RUN mkdir -p /app/staticfiles

# Verify static assets exist before collecting (fails build if images are missing)
RUN test -f /app/static/images/hubsign_logo.png || (echo "ERROR: hubsign_logo.png not found in build context" && exit 1)
RUN test -f /app/static/images/fepro_logo.png   || (echo "ERROR: fepro_logo.png not found in build context" && exit 1)

# Set build-time env so collectstatic runs in production mode
ENV DJANGO_SETTINGS_MODULE=hubsign.settings \
    DEBUG=False \
    SECRET_KEY=build-time-placeholder-overridden-at-runtime

# Collect static files
RUN python manage.py collectstatic --noinput --clear --verbosity 2

# Create non-root user for security
RUN useradd -m -u 1000 hubsign && \
    chown -R hubsign:hubsign /app
USER hubsign

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/')"

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "hubsign.wsgi:application"]
