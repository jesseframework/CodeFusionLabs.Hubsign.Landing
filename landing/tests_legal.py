"""Tests for the legal pages and the site's privacy posture.

The cookie-free result is the load-bearing one: it is the reason this site does
not need a consent banner. If a future change starts setting a cookie or pulls
in a third-party origin, these fail.
"""
import re
from pathlib import Path

from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from landing import legal
from landing.company import COMPANY, REQUIRED_BEFORE_PUBLISH, Unknown, is_publishable
from landing.pricing import (
    _fallback_tiers,
    annual_saving_percent,
    max_annual_saving_percent,
)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / 'templates'


class CookiePostureTests(TestCase):
    """No cookies means no consent banner is required. Keep it that way."""

    PAGES = ['landing:index', 'landing:privacy', 'landing:terms',
             'landing:cookies', 'landing:refunds', 'landing:accessibility']

    def test_no_page_sets_a_cookie(self):
        for name in self.PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(
                    list(response.cookies.keys()), [],
                    'This page set a cookie. The cookie policy at /legal/cookies/ '
                    'states that the site sets none, and no consent banner exists.',
                )

    def test_csrf_cookie_is_not_forced_by_a_template(self):
        """base.html used to emit <meta name="csrf-token" content="{{ csrf_token }}">.

        Reading csrf_token in a template makes Django set the csrftoken cookie on
        every page load -- on a site with no forms and no state-changing fetches.
        """
        response = self.client.get(reverse('landing:index'))
        self.assertNotIn('csrftoken', response.cookies)
        self.assertNotIn('csrf-token', response.content.decode())


class ThirdPartyOriginTests(TestCase):
    """The site must stay free of third-party requests."""

    BANNED = [
        'fonts.googleapis.com', 'fonts.gstatic.com',
        'googletagmanager', 'google-analytics', 'gtag(',
        'plausible.io', 'posthog', 'hotjar', 'segment.com', 'mixpanel',
        'intercom', 'drift.com', 'facebook.net', 'doubleclick',
        'cdn.jsdelivr.net', 'unpkg.com', 'cdnjs.cloudflare.com',
    ]

    def test_templates_reference_no_third_party_origin(self):
        for path in TEMPLATES.rglob('*'):
            if not path.is_file():
                continue
            text = path.read_text(encoding='utf-8')
            for needle in self.BANNED:
                with self.subTest(file=path.name, needle=needle):
                    self.assertNotIn(needle, text)

    def test_stylesheet_loads_only_local_fonts(self):
        css = (ROOT / 'static' / 'css' / 'main.css').read_text(encoding='utf-8')
        for url in re.findall(r'url\((.*?)\)', css):
            self.assertTrue(
                url.strip('"\'').startswith('../fonts/'),
                f'stylesheet fetches {url}; everything must be self-hosted',
            )

    def test_font_files_and_their_licences_are_present(self):
        fonts = ROOT / 'static' / 'fonts'
        for name in ('inter-400-700', 'fraunces-wonk', 'ibm-plex-mono-500'):
            self.assertTrue((fonts / f'{name}.woff2').exists(), f'missing {name}.woff2')
        # All three families are OFL 1.1; redistribution requires shipping the licence.
        for licence in ('OFL-inter.txt', 'OFL-fraunces.txt', 'OFL-ibm-plex-mono.txt'):
            self.assertTrue((fonts / licence).exists(), f'missing {licence}')


class SecurityHeaderTests(TestCase):
    def test_csp_header_is_actually_sent(self):
        """The old CSP_* settings were django-csp 3.x style and were silently
        ignored by 4.x, so no policy was being sent at all."""
        response = self.client.get(reverse('landing:index'))
        csp = response.headers.get('Content-Security-Policy', '')
        self.assertTrue(csp, 'no Content-Security-Policy header')
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)

    def test_script_src_forbids_inline(self):
        csp = self.client.get(reverse('landing:index')).headers['Content-Security-Policy']
        script = next(d for d in csp.split(';') if d.strip().startswith('script-src'))
        self.assertNotIn('unsafe-inline', script)

    def test_other_security_headers(self):
        headers = self.client.get(reverse('landing:index')).headers
        self.assertEqual(headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertEqual(headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(headers.get('X-Frame-Options'), 'DENY')
        self.assertIn('camera=()', headers.get('Permissions-Policy', ''))


class LegalRoutingTests(TestCase):
    def test_all_legal_pages_resolve_and_render(self):
        for page in legal.LEGAL_PAGES:
            with self.subTest(page=page['title']):
                response = self.client.get(reverse(page['url_name']))
                self.assertEqual(response.status_code, 200)
                # Titles containing '&' are HTML-escaped in the rendered page.
                self.assertContains(response, escape(page['title']))

    def test_footer_links_to_every_legal_page_from_the_landing_page(self):
        html = self.client.get(reverse('landing:index')).content.decode()
        for page in legal.LEGAL_PAGES:
            self.assertIn(reverse(page['url_name']), html)

    def test_dead_routes_no_longer_500(self):
        """/pricing/ and /features/ rendered templates that never existed."""
        self.assertEqual(self.client.get('/pricing/').status_code, 302)
        self.assertEqual(self.client.get('/features/').status_code, 404)

    def test_removed_lead_capture_endpoints_are_gone(self):
        """Both accepted PII from anyone, logged it in plaintext and stored nothing."""
        self.assertEqual(self.client.post('/api/contact/', {}).status_code, 404)
        self.assertEqual(self.client.post('/api/newsletter/', {}).status_code, 404)

    def test_robots_and_sitemap(self):
        robots = self.client.get('/robots.txt')
        self.assertEqual(robots.status_code, 200)
        self.assertIn('Disallow: /admin/', robots.content.decode())

        sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(sitemap.status_code, 200)
        body = sitemap.content.decode()
        for page in legal.LEGAL_PAGES:
            self.assertIn(reverse(page['url_name']), body)

    def test_api_docs_are_not_public_by_default(self):
        self.assertEqual(self.client.get('/api/docs/').status_code, 404)
        self.assertEqual(self.client.get('/api/schema/').status_code, 404)


class CompanyDetailTests(TestCase):
    def test_unresolved_details_are_left_out_not_shown_as_markers(self):
        """Preliminary release: an unconfirmed detail is omitted from public
        pages (never invented, never printed as a placeholder). The system
        check still reports it -- see test_placeholder_state_matches_the_system_check."""
        for key in REQUIRED_BEFORE_PUBLISH:
            if isinstance(COMPANY[key], Unknown):
                break
        else:
            self.skipTest('all details confirmed')
        for name in ('landing:index', 'landing:privacy', 'landing:terms', 'landing:accessibility'):
            html = self.client.get(reverse(name)).content.decode()
            self.assertNotIn('NEEDS CONFIRMATION', html, name)
            self.assertNotIn('needs-confirmation', html, name)

    def test_placeholder_state_matches_the_system_check(self):
        from landing.checks import check_company_details
        warnings = check_company_details(None)
        self.assertEqual(bool(warnings), not is_publishable())

    def test_footer_shows_the_legal_entity_and_jurisdiction(self):
        html = self.client.get(reverse('landing:index')).content.decode()
        self.assertIn(COMPANY['legal_name'], html)
        self.assertIn(COMPANY['jurisdiction'], html)

    def test_phone_is_a_dialable_link(self):
        """+1 810-626-EDGE is not dialable on every device."""
        html = self.client.get(reverse('landing:index')).content.decode()
        self.assertIn(f'tel:{COMPANY["phone_tel"]}', html)


class MarketingClaimTests(TestCase):
    def test_no_unscoped_compliance_claim(self):
        """The meta description used to read 'Fully compliant digital signatures'
        without naming a single standard."""
        html = self.client.get(reverse('landing:index')).content.decode().lower()
        for phrase in ('fully compliant', 'legally binding', '256-bit',
                       'bank-level', 'military-grade', 'soc 2', 'hipaa'):
            self.assertNotIn(phrase, html, f'unsubstantiated claim: {phrase!r}')

    def test_no_testimonials_or_customer_counts(self):
        html = self.client.get(reverse('landing:index')).content.decode().lower()
        for phrase in ('trusted by', 'customers worldwide', 'join thousands'):
            self.assertNotIn(phrase, html)

    def test_annual_saving_badge_is_not_overstated(self):
        """A flat 'Save 20%' overstated Business and Enterprise Shared, which
        both save 17%. The badge is derived from the real prices instead."""
        tiers = _fallback_tiers()
        claimed = max_annual_saving_percent(tiers)
        html = self.client.get(reverse('landing:index')).content.decode()
        self.assertIn(f'Save up to {claimed}%', html)
        for tier in tiers:
            self.assertLessEqual(
                annual_saving_percent(tier), claimed,
                f'{tier.name} saves more than the advertised maximum',
            )

    def test_annual_saving_is_truthful_per_tier(self):
        by_id = {t.id: annual_saving_percent(t) for t in _fallback_tiers()}
        self.assertEqual(by_id['starter'], 20)
        self.assertEqual(by_id['business'], 17)
        self.assertEqual(by_id['enterprise'], 17)

    def test_trademark_attribution_present(self):
        """Third-party product names appear in the integrations section."""
        html = self.client.get(reverse('landing:index')).content.decode()
        self.assertIn('property of their respective owners', html)


class PricingRenderTests(TestCase):
    def test_both_price_sets_are_server_rendered(self):
        """The billing toggle must not depend on /api/pricing/ resolving; it
        previously left monthly figures visible under an 'Annual' label."""
        html = self.client.get(reverse('landing:index')).content.decode()
        amounts = re.findall(r'<span class="pricing-amount num"\s+data-monthly="(\d+)"\s+data-annual="(\d+)"', html)
        self.assertEqual(len(amounts), 6)
        for monthly, annual in amounts:
            self.assertLess(int(annual), int(monthly))

    def test_free_tier_is_not_shown_as_a_card(self):
        html = self.client.get(reverse('landing:index')).content.decode()
        self.assertNotIn('data-tier="free"', html)
