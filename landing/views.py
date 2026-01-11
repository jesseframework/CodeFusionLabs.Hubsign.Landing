from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings


class IndexView(TemplateView):
    """Main landing page view."""
    template_name = 'landing/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shared_instance'] = settings.HUBSIGN_SHARED_INSTANCE
        context['pricing_tiers'] = self.get_pricing_tiers()
        context['features'] = self.get_features()
        return context
    
    def get_pricing_tiers(self):
        """Return pricing tier data."""
        return [
            {
                'name': 'Personal',
                'price': 'Free',
                'period': '',
                'description': 'For casual signers. Free forever.',
                'features': [
                    'Up to 3 docs/month',
                    'Unlimited recipients',
                    'No credit card',
                ],
                'featured': False,
                'cta': 'Get Started',
            },
            {
                'name': 'Individual',
                'price': '$15',
                'period': '/mo',
                'description': 'Unlimited signing for individuals.',
                'features': [
                    'Unlimited documents',
                    'API access',
                    'Email support',
                ],
                'featured': True,
                'cta': 'Get Started',
            },
            {
                'name': 'Business',
                'price': '$60',
                'period': '/mo',
                'description': 'Shared workspace for 5 users.',
                'features': [
                    '+$8/user for more',
                    'API + Automation',
                    'Embedding',
                ],
                'featured': False,
                'cta': 'Get Started',
            },
            {
                'name': 'Enterprise',
                'price': '$200',
                'period': '/mo',
                'description': 'Dedicated for your business.',
                'features': [
                    'Custom domain',
                    'Unlimited teams',
                    'SMTP + OAuth',
                ],
                'featured': False,
                'cta': 'Get Started',
            },
        ]
    
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
        context['pricing_tiers'] = IndexView().get_pricing_tiers()
        return context


class FeaturesView(TemplateView):
    """Features page view."""
    template_name = 'landing/features.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['features'] = IndexView().get_features()
        return context
