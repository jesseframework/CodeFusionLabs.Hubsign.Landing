"""
URL configuration for HubSign Landing project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Landing pages
    path('', include('landing.urls')),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Enable browser reload in DEBUG mode
if settings.DEBUG:
    urlpatterns = [
        path("__reload__/", include("django_browser_reload.urls")),
    ] + urlpatterns
