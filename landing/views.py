from django.shortcuts import render
from django.views.generic import TemplateView

from .pricing import get_pricing_tiers


class IndexView(TemplateView):
    """Main landing page view."""
    template_name = 'landing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricing_tiers'] = get_pricing_tiers()
        context['feature_bands'] = self.get_feature_bands()
        return context

    def get_feature_bands(self):
        """3-band feature catalogue (Signing / Document Manager / Automation)
        for the compact Features overview grid.

        Tier-gating badges and the Automation banner copy are sourced from
        HubSign-Pricing-Plan.md Section 2 ("Proposed full ladder" / "Feature
        differentiation"): API + embedding is Business-tier-and-up only, and
        SSO/custom domain are Enterprise Dedicated only -- both gated, not
        free everywhere, unlike Workflow Builder which the doc confirms is
        unlimited on every tier including Free. Approval engine, SLA
        tracking, and Branding/reporting aren't covered by that doc and are
        left unqualified pending confirmation of their tier-gating.
        """
        return [
            {
                'id': 'signing', 'label': 'Signing', 'columns': 2,
                'title': 'Everything you need to sign at scale',
                'cards': [
                    {
                        'title': '11 field types', 'icon': 'edit',
                        'description': 'Signature, initials, date, dropdown, checkbox and more — with validation rules.',
                    },
                    {
                        'title': 'Recipient roles', 'icon': 'users',
                        'description': 'Signer, approver, viewer, CC and assistant — routed in the order you set.',
                    },
                    {
                        'title': 'Bulk send', 'icon': 'bulk-send',
                        'description': 'CSV mail-merge against a template — one document per row.',
                    },
                    {
                        'title': 'Direct templates', 'icon': 'link',
                        'description': 'Public self-serve signing links and a shareable profile page.',
                    },
                ],
            },
            {
                'id': 'dms', 'label': 'Document Manager', 'columns': 2,
                'title': 'More than e-signatures. A complete DMS.',
                'cards': [
                    {
                        'title': 'Filing and retention', 'icon': 'document',
                        'description': 'Locations, cabinets, shelves and bins. Auto-filing rules, retention and disposal policies.',
                    },
                    {
                        'title': 'Smart OCR search', 'icon': 'search',
                        'description': 'Machine-learning text extraction makes scanned pages findable by content.',
                    },
                    {
                        'title': 'Version control', 'icon': 'version',
                        'description': 'Check-out and check-in prevents conflicting edits. Full audit trail on every action.',
                    },
                    {
                        'title': 'Ask your archive', 'icon': 'sparkle',
                        'description': 'An AI assistant that answers questions and builds reports over your filed documents.',
                    },
                ],
            },
            {
                'id': 'automation', 'label': 'Automation', 'columns': 3,
                'title': 'The work around the signature, handled',
                'banner': 'Workflow automation starts on Free. Volume, users and advanced integrations scale with your plan.',
                'cards': [
                    {
                        'title': 'Workflow builder', 'icon': 'workflow', 'featured': True,
                        'description': 'No-code automation on 12 events or a schedule. Describe it in plain English and it builds itself.',
                    },
                    {
                        'title': 'Approval engine', 'icon': 'approval',
                        'description': 'Approval templates, role mappings, member hierarchy and override routing.',
                    },
                    {
                        'title': 'SLA tracking', 'icon': 'clock',
                        'description': 'Business-hours-aware targets, breach detection and dashboards.',
                    },
                    {
                        'title': 'API, webhooks, Teams', 'icon': 'api', 'badge': 'Business & up',
                        'description': 'Full REST API, signed webhooks on 7 events, and native Teams notifications.',
                    },
                    {
                        'title': 'SSO and domain control', 'icon': 'lock', 'badge': 'Enterprise Dedicated',
                        'description': 'Per-org OIDC with auto-provisioning, allowed email domains, signup control.',
                    },
                    {
                        'title': 'Branding and reporting', 'icon': 'branding',
                        'description': 'Your logo and colors on signing pages and emails. Build your own reports.',
                    },
                ],
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
        context['feature_bands'] = IndexView().get_feature_bands()
        return context
