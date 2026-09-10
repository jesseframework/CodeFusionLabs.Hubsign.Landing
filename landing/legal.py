"""Legal and policy pages.

These are drafts. HubSign-Pricing-Plan.md section 6 already records that the
commercial terms "need a short conversation with counsel before terms are
published -- particularly for Individual, where buyers are consumers rather
than businesses". That applies to every page here.

While ``REVIEW_PENDING`` is True each page carries a visible review banner.
Flip it to False in one place once counsel has signed off.

Jurisdiction: Future Edge Technology Inc. is an Ontario company, so the privacy
pages are built on PIPEDA (federal) with Quebec Law 25 additions, and the terms
choose Ontario law. Visitors from the EU/UK get GDPR/UK GDPR disclosures; the
Jamaican operation is covered by the Data Protection Act 2020.
"""
import datetime

from django.views.generic import TemplateView

# Bump when a policy's substance changes, not for typo fixes.
LAST_UPDATED = datetime.date(2026, 9, 8)

# Set to False once counsel has reviewed these documents. This removes the
# review banner from every legal page at once.
REVIEW_PENDING = True


class LegalPageView(TemplateView):
    """Shared plumbing for the /legal/ pages."""

    #: Shown in <title>, the page heading and the legal-page navigation.
    page_title = ''
    #: Meta description for this page.
    page_description = ''
    #: One line under the heading explaining what the document covers.
    page_summary = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title=self.page_title,
            page_description=self.page_description,
            page_summary=self.page_summary,
            last_updated=LAST_UPDATED,
            review_pending=REVIEW_PENDING,
            legal_pages=LEGAL_PAGES,
            current_page=self.__class__.__name__,
        )
        return context


class PrivacyView(LegalPageView):
    template_name = 'legal/privacy.html'
    page_title = 'Privacy Policy'
    page_description = (
        'How Future Edge Technology Inc. handles personal information on the HubSign '
        'website, under PIPEDA, Quebec Law 25 and the GDPR.'
    )
    page_summary = (
        'What this website collects, what it does not, and the rights you have over '
        'information about you.'
    )


class TermsView(LegalPageView):
    template_name = 'legal/terms.html'
    page_title = 'Website Terms of Use'
    page_description = (
        'The terms governing use of the HubSign marketing website at hubsign.io. '
        'Use of the HubSign application is governed separately.'
    )
    page_summary = (
        'These terms cover this website only. Your use of the HubSign application is '
        'governed by the subscription agreement you accept when you create an account.'
    )


class CookiesView(LegalPageView):
    template_name = 'legal/cookies.html'
    page_title = 'Cookie Policy'
    page_description = (
        'This website sets no cookies of its own and runs no analytics or advertising '
        'trackers. What that means, and the one infrastructure cookie involved.'
    )
    page_summary = 'A short policy, because there is very little to disclose.'


class RefundsView(LegalPageView):
    template_name = 'legal/refunds.html'
    page_title = 'Cancellation & Refunds'
    page_description = (
        'How cancellation and refunds work for HubSign subscriptions, and the statutory '
        'rights that apply regardless.'
    )
    page_summary = 'How to cancel, and what happens to money already paid.'


class AccessibilityView(LegalPageView):
    template_name = 'legal/accessibility.html'
    page_title = 'Accessibility Statement'
    page_description = (
        'HubSign\u2019s accessibility commitment, the standard this website targets, known '
        'limitations, and how to report a barrier.'
    )
    page_summary = (
        'What this site aims for, where it currently falls short, and how to tell us '
        'when something does not work.'
    )


#: Drives the footer legal column and the cross-links between legal pages.
LEGAL_PAGES = [
    {'url_name': 'landing:privacy', 'title': PrivacyView.page_title, 'view': 'PrivacyView'},
    {'url_name': 'landing:terms', 'title': TermsView.page_title, 'view': 'TermsView'},
    {'url_name': 'landing:cookies', 'title': CookiesView.page_title, 'view': 'CookiesView'},
    {'url_name': 'landing:refunds', 'title': RefundsView.page_title, 'view': 'RefundsView'},
    {'url_name': 'landing:accessibility', 'title': AccessibilityView.page_title, 'view': 'AccessibilityView'},
]
