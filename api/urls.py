from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Contact/Lead endpoints
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('newsletter/', views.NewsletterSignupView.as_view(), name='newsletter'),
    
    # Public info endpoints
    path('pricing/', views.PricingInfoView.as_view(), name='pricing-info'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]
