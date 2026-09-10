"""Views for the HubSign landing page."""
from django.views.generic import TemplateView

from .pricing import get_pricing_tiers, max_annual_saving_percent

# The product pipeline, in order. Drawn full-size once as the hero diagram and
# reused as a small position marker on each section, so both always describe the
# same six steps. `commodity` marks the step every e-signature vendor sells --
# the one the page argues is the least interesting part.
PIPELINE = [
    {'id': 'arrives', 'label': 'Arrives', 'group': 'Intake',
     'detail': 'A vendor emails the invoice, exactly as they do today.'},
    {'id': 'reads', 'label': 'Reads', 'group': 'Intake',
     'detail': 'OCR extracts the data before anyone opens the document.'},
    {'id': 'checks', 'label': 'Checks', 'group': 'Control',
     'detail': 'Business rules test the data against the limits you set.'},
    {'id': 'routes', 'label': 'Routes', 'group': 'Control',
     'detail': 'Approval chains collect internal sign-off first.'},
    {'id': 'seals', 'label': 'Seals', 'group': 'Signature', 'commodity': True,
     'detail': 'The signature itself, with its certificate and audit report.'},
    {'id': 'posts', 'label': 'Posts', 'group': 'Connect',
     'detail': 'The result lands in the ERP, in Teams, or in your own systems.'},
]


class IndexView(TemplateView):
    """Main landing page view."""
    template_name = 'landing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricing_tiers'] = get_pricing_tiers()
        context['stats'] = self.get_stats()
        context['pillars'] = self.get_pillars()
        context['field_types'] = self.get_field_types()
        context['roles'] = self.get_roles()
        context['integrations'] = self.get_integrations()
        context['faqs'] = self.get_faqs()
        context['spine'] = PIPELINE
        # Free is deliberately not shown as a card (asserted in landing/tests.py);
        # the two visible families are Starter/Plus/Pro and Team/Business/Enterprise.
        tiers = context['pricing_tiers']
        context['pricing_groups'] = [
            ('individual', tiers[1:4]),
            ('organization', tiers[4:7]),
        ]
        # Derived, not hardcoded -- see pricing.max_annual_saving_percent for
        # why the old flat "Save 20%" badge was inaccurate.
        context['annual_saving'] = max_annual_saving_percent(context['pricing_tiers'])
        return context

    def get_stats(self):
        return [
            {'n': '10', 'label': 'signable field types'},
            {'n': '5', 'label': 'recipient roles'},
            {'n': '7', 'label': 'webhook events'},
            {'n': '4', 'label': 'SSO providers'},
        ]

    def get_pillars(self):
        """The 'four capabilities' overview -- Intake/Control/Records around the
        commodity e-signature middle, plus Connect for the systems it posts to."""
        return [
            {
                'icon': 'intake', 'title': 'Intake', 'subtitle': 'Email-to-sign, with OCR',
                'description': 'Vendors keep emailing invoices exactly as they do today. The queue reads them on arrival — before anyone opens the document.',
                'tags': ['Signature Inbox', 'OCR confidence scoring', 'Per-attachment queueing'],
            },
            {
                'icon': 'control', 'title': 'Control', 'subtitle': 'Rules, approvals, workflows',
                'description': 'Refuse a signature when the data is wrong. Route internal sign-off first. Automate what happens next.',
                'tags': ['Business Rules (JSONLogic)', 'Approval chains', 'Workflow engine'],
            },
            {
                'icon': 'records', 'title': 'Records', 'subtitle': 'Filing, retention, retrieval',
                'description': 'Keep what was signed — filed, classified and retained on schedule. For physical files as well as digital.',
                'tags': ['Filing structure', 'Retention & disposal', 'Retrieval requests'],
            },
            {
                'icon': 'connect', 'title': 'Connect', 'subtitle': 'Webhooks, REST, ERP posting',
                'description': 'Turn a signature into a transaction. Post to the ERP, notify Teams, or let your systems pull the result.',
                'tags': ['Webhooks · 7 events', 'REST API v1 + v2 beta', 'Workflow HTTP requests'],
            },
        ]

    def get_field_types(self):
        return [
            'Signature', 'Initials', 'Name', 'Email', 'Date',
            'Text', 'Number', 'Checkbox', 'Radio', 'Dropdown',
        ]

    def get_roles(self):
        return [
            {'name': 'Signer', 'desc': 'Fills fields and signs'},
            {'name': 'Approver', 'desc': 'Approves without signature fields'},
            {'name': 'Viewer', 'desc': 'Must open the document; adds no marks'},
            {'name': 'CC', 'desc': 'Receives the finished copy only'},
            {'name': 'Assistant', 'desc': 'Fills fields on behalf of another recipient, who then signs'},
        ]

    # The 9 showcase-carousel panels aren't uniform repeatable cards -- each
    # is a bespoke mini-screen -- so they're hardcoded directly in
    # templates/landing/index.html rather than looped from context here.

    def get_integrations(self):
        """Grouped rather than flat.

        As a single eight-card grid, Azure AD / Google Workspace / Okta / Auth0
        all rendered with the same generic key icon and the same one-line
        description, so a quarter of the section read as four identical cards.
        Grouping says the useful thing once, in the group heading.
        """
        return [
            {
                'title': 'Microsoft 365',
                'note': 'where the work already happens',
                'items': [
                    {'icon': 'teams', 'title': 'Microsoft Teams',
                     'description': 'Power Automate webhook or an Azure bot, per channel'},
                    {'icon': 'intake', 'title': 'Exchange Online',
                     'description': 'Where the Signature Inbox mailbox lives'},
                ],
            },
            {
                'title': 'Single sign-on',
                'note': 'OIDC · 4 providers',
                'items': [
                    {'icon': 'sso-key', 'title': 'Microsoft Entra ID',
                     'description': 'Formerly Azure AD'},
                    {'icon': 'sso-key', 'title': 'Google Workspace', 'description': ''},
                    {'icon': 'sso-key', 'title': 'Okta', 'description': ''},
                    {'icon': 'sso-key', 'title': 'Auth0', 'description': ''},
                ],
            },
            {
                'title': 'Build your own',
                'note': 'for anything not listed above',
                'items': [
                    {'icon': 'webhook', 'title': 'Webhooks',
                     'description': '7 events, delivered on completion'},
                    {'icon': 'rest-api', 'title': 'REST API',
                     'description': 'v1 stable, v2 in beta'},
                ],
            },
        ]

    def get_faqs(self):
        return [
            {
                'q': 'Does OCR replace someone checking the invoice?',
                'a': 'No — extracted data opens beside the original with a confidence score and a needs-review flag, so review means checking, not retyping.',
            },
            {
                'q': 'What happens when a business rule blocks a signature?',
                'a': "The document is stopped before the signature is recorded, with a message that tells the signer what to fix. Rule evaluation fails open by design, so one bad rule can't stop every signature in the organization.",
            },
            {
                'q': 'Can HubSign post signed documents into our ERP?',
                'a': "Yes — a workflow's HTTP_REQUEST step calls out once the document is sealed. For guaranteed delivery, pair a webhook with your own middleware.",
            },
            {
                'q': "What's actually in the audit certificate?",
                'a': "A Final Audit Report appended to the sealed PDF, recording who signed, when, from where, and the document's integrity hash — verifiable from the QR code and share link on the certificate.",
            },
            {
                'q': 'Does Doc Manager handle physical, paper records too?',
                'a': 'Yes. A record can be digital, physical, or both, with a filing address — location, cabinet, shelf, bin — shared between the scanned copy and the shelf it sits on.',
            },
            {
                'q': 'Do you support single sign-on?',
                'a': 'Yes — OIDC against Azure AD, Google Workspace, Okta, or Auth0. Members sign in at your org URL, and self-signup can be restricted to your domain.',
            },
            {
                'q': 'Can I start small?',
                'a': 'Yes. Starter is $15/month with no organization rollout required. Move to Plus or Pro as signing volume grows, or contact sales for Team, Business, or Enterprise Shared.',
            },
        ]
