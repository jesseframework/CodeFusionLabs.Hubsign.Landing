from django.shortcuts import render
from django.views.generic import TemplateView

from .pricing import get_pricing_tiers


class IndexView(TemplateView):
    """Main landing page view."""
    template_name = 'landing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricing_tiers'] = get_pricing_tiers()
        context['features'] = self.get_features()
        return context

    def get_features(self):
        """Return feature list data."""
        return [
            {
                'title': 'Easy Signing',
                'description': 'Sign documents in seconds with draw, type, or upload.',
                'icon': 'edit',
            },
            {
                'title': 'Templates',
                'description': 'Create reusable templates with one-click workflows.',
                'icon': 'document',
            },
            {
                'title': 'Teams',
                'description': 'Collaborate and manage permissions securely.',
                'icon': 'users',
            },
            {
                'title': 'Direct Links',
                'description': 'Share signing links without account creation.',
                'icon': 'link',
            },
            {
                'title': 'Secure',
                'description': '256-bit encryption with complete audit trails.',
                'icon': 'lock',
            },
            {
                'title': 'Lightning Fast',
                'description': 'Send and receive signed documents in seconds.',
                'icon': 'clock',
            },
        ]


class PricingView(TemplateView):
    """Pricing page view."""
    template_name = 'landing/pricing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricing_tiers'] = get_pricing_tiers()
        return context


class FeaturesView(TemplateView):
    """Features page view."""
    template_name = 'landing/features.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['features'] = IndexView().get_features()
        return context
