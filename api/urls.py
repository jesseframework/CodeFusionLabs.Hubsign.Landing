from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/lookup/', views.TenantLookupView.as_view(), name='tenant-lookup'),
    path('auth/signin/', views.SignInRequestView.as_view(), name='signin-request'),
    path('auth/verify/', views.VerifyMagicLinkView.as_view(), name='verify-magic-link'),
    
    # Contact/Lead endpoints
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('newsletter/', views.NewsletterSignupView.as_view(), name='newsletter'),
    
    # Public info endpoints
    path('pricing/', views.PricingInfoView.as_view(), name='pricing-info'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]
