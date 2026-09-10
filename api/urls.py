from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    # Public info endpoints. The contact/ and newsletter/ endpoints that used to
    # live here were removed: nothing on the site posted to them, they accepted
    # PII from anyone, logged it in plaintext and stored nothing. See
    # /legal/privacy/ -- the site collects no personal information.
    path('pricing/', views.PricingInfoView.as_view(), name='pricing-info'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]
