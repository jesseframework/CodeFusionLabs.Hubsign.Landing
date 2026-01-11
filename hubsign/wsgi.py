"""
WSGI config for HubSign Landing project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hubsign.settings')
application = get_wsgi_application()
