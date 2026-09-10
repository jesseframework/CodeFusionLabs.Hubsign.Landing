"""
URL configuration for HubSign Landing project.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from landing.sitemap import SitemapView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Landing pages
    path('', include('landing.urls')),

    # API endpoints
    path('api/', include('api.urls')),

    path(
        'robots.txt',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain'),
        name='robots',
    ),
    path('sitemap.xml', SitemapView.as_view(), name='sitemap'),
]

# The OpenAPI schema and Swagger UI enumerate the API surface. They are of no
# use on a marketing site, so they are off unless EXPOSE_API_DOCS is set.
if settings.EXPOSE_API_DOCS:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]

# Enable browser reload in DEBUG mode
if settings.DEBUG:
    urlpatterns = [
        path('__reload__/', include('django_browser_reload.urls')),
    ] + urlpatterns
