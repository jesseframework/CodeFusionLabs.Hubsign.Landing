from django.urls import path
from django.views.generic import RedirectView

from . import legal, views

app_name = 'landing'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    # /pricing/ and /features/ used to route to PricingView and FeaturesView,
    # whose templates never existed -- both returned HTTP 500. Everything lives
    # on the single page now; /pricing/ redirects in case it is linked
    # externally, and /features/ was never linked at all.
    path('pricing/', RedirectView.as_view(url='/#pricing', permanent=False), name='pricing'),

    # Legal
    path('legal/privacy/', legal.PrivacyView.as_view(), name='privacy'),
    path('legal/terms/', legal.TermsView.as_view(), name='terms'),
    path('legal/cookies/', legal.CookiesView.as_view(), name='cookies'),
    path('legal/refunds/', legal.RefundsView.as_view(), name='refunds'),
    path('legal/accessibility/', legal.AccessibilityView.as_view(), name='accessibility'),
]
