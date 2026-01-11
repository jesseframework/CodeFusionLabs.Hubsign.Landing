from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health'),
    
    # Tenant/Subdomain validation
    path('tenant/validate/', views.validate_tenant, name='validate_tenant'),
    
    # Authentication
    path('auth/magic-link/', views.send_magic_link, name='magic_link'),
    path('auth/signup/', views.signup, name='signup'),
]
