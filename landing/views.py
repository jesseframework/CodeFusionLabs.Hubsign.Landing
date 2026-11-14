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


# The "See it in action" carousel (section id="showcase"). Real, anonymised
# screenshots (static/images/screens/, fictional "Meridian Motors" data) --
# not CSS skeleton geometry -- so each entry carries real alt text as well as
# the caption shown in the aria-live region. Order follows the page's six-step
# spine (Arrives/Reads -> inbox, invoice-detail; Checks -> business-rules,
# duplicate-blocked; Seals -> esign; Posts -> workflows) and then the three
# measurement screens.
#
# Every image is a 2:1 crop of the real screen (no sidebar or header chrome),
# so the frame can show it edge to edge with nothing empty around it. Two of
# the screens were too short to fill 2:1 on their own, so they were extended
# with more of the same: the blocked invoice's timeline gained three events
# (rule held it, vendor and AP team emailed) and the reports list gained five
# smaller vendors, with its totals recalculated to match. Workflows is stacked
# on Email Templates, the other half of the same Automation settings group, and
# the rules list drops a duplicated rule. Images are only ever scaled down in
# the browser, never up, so text stays sharp. Approval Templates is not in the
# carousel: its only content is a heading and one table row.
SHOWCASE = [
    {
        'title': 'Signature Inbox',
        'blurb': 'Every vendor invoice lands here, already read by OCR before anyone opens it.',
        'alt': 'The Signature Inbox: six vendor invoices with OCR-read invoice numbers and PO '
               'references, vendor, amounts, dates and who is responsible — some overdue, one '
               'already signed.',
        'image': 'inbox-crop', 'width': 1600, 'height': 800,
    },
    {
        'title': 'Extracted data',
        'blurb': 'OCR fields with a confidence score, beside the original — the attached PO is read too.',
        'alt': 'An open invoice: extracted OCR fields with confidence percentages on the left; '
               'on the right, the signing status, the purchase order read from the signer '
               'attachment, and the start of the activity timeline.',
        'image': 'invoice-detail-crop', 'width': 1600, 'height': 800,
    },
    {
        'title': 'Business rules',
        'blurb': 'Rules that refuse a signature outright when the data is wrong.',
        'alt': 'Business Rules settings: five rules — low OCR confidence, duplicate invoice, '
               'missing supporting document, attached PO mismatch and missing PO number — each '
               'set to BLOCK with a JSONLogic condition, above a box for testing rules against '
               'a document.',
        'image': 'business-rules-crop', 'width': 1309, 'height': 666,
    },
    {
        'title': 'A rule fires',
        'blurb': 'A duplicate is caught before anyone signs — the vendor and team are notified automatically.',
        'alt': 'An invoice held by the duplicate rule: the signing panel with the signer not yet '
               'signed, and a timeline showing the rule holding the invoice and the vendor and '
               'AP team being emailed.',
        'image': 'duplicate-blocked-crop', 'width': 1600, 'height': 800,
    },
    {
        'title': 'Signing',
        'blurb': 'Every document, by state — draft, out for signature, or completed.',
        'alt': 'The E-Sign list: summary cards for total, pending, completed and draft documents '
               'above a table of documents with their recipients and status.',
        'image': 'esign-crop', 'width': 1602, 'height': 801,
    },
    {
        'title': 'Automation',
        'blurb': 'What happens next, triggered by events — nothing re-keyed.',
        'alt': 'Automation settings: two enabled workflows, one triggered when a duplicate '
               'invoice is detected and one when OCR processing completes, above the reusable '
               'email templates those workflows send.',
        'image': 'workflows-crop', 'width': 1354, 'height': 676,
    },
    {
        'title': 'Tracking',
        'blurb': 'Volume, status and signature ageing, for the whole workspace, live.',
        'alt': 'The dashboard: totals for documents, open approvals, awaiting signature and '
               'completed, with a document-status donut, monthly trend, signature ageing and '
               'document source charts.',
        'image': 'dashboard-crop', 'width': 1602, 'height': 801,
    },
    {
        'title': 'SLA',
        'blurb': 'Turnaround measured against target — internal time kept separate from end-to-end.',
        'alt': 'The SLA page: a health score of 43 marked critical, internal-turnaround versus '
               'end-to-end on-time percentages, an on-time trend, and invoices overdue and '
               'still unsent.',
        'image': 'sla-crop', 'width': 1600, 'height': 800,
    },
    {
        'title': 'Reports',
        'blurb': 'Spend by vendor, checked against the limit — overruns highlighted.',
        'alt': 'The Reports page: total spend against limit, then spend by vendor — three '
               'vendors over their limit shown in red, five within it shown in green.',
        'image': 'reports-crop', 'width': 1600, 'height': 800,
    },
]
for _panel in SHOWCASE:
    _panel['png'] = 'images/screens/{}.png'.format(_panel['image'])
    _panel['webp'] = 'images/screens/{}.webp'.format(_panel['image'])
# Each panel's "Next: ..." prompt names the following screen; the last one
# wraps back to the first.
for _i, _panel in enumerate(SHOWCASE):
    _panel['next_title'] = SHOWCASE[(_i + 1) % len(SHOWCASE)]['title']


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
        context['showcase'] = SHOWCASE
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
        """Kept factual -- these are counts that already exist elsewhere on the
        page (field types, roles, webhook events, SSO providers) -- but worded
        as capabilities rather than a spec sheet, with an 'At a glance' eyebrow
        in the template so the band reads as a summary, not a KPI row."""
        return [
            {'n': '10', 'label': 'field types you can place'},
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
                # Subtitle names the in-app feature (Repositories) rather than
                # repeating "Records" -- the FAQ and this card used to call the
                # same feature three different things (Records / Doc Manager /
                # Document Manager). Repositories is the one name the app uses.
                'icon': 'records', 'title': 'Records', 'subtitle': 'The Repositories feature',
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
                'q': 'Does Repositories handle physical, paper records too?',
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
