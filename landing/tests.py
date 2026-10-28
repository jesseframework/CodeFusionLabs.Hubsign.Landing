import re
from unittest.mock import patch

from django.test import TestCase, override_settings

from .pricing import _fallback_tiers, get_pricing_tiers


class FakePrice:
    def __init__(self, d):
        self._d = d

    def to_dict(self):
        return self._d


class FakeSearchResult:
    def __init__(self, data):
        self.data = data


def fake_price(unit_amount, interval, price_id, **metadata):
    return FakePrice({
        'id': price_id,
        'unit_amount': unit_amount,
        'recurring': {'interval': interval},
        'product': {'active': True, 'metadata': metadata},
    })


class PricingFallbackTests(TestCase):
    """BILLING_ENABLED is False by default (no STRIPE_API_KEY in test settings),
    so get_pricing_tiers() should always return the hardcoded fallback here."""

    def test_default_settings_return_fallback_tiers(self):
        tiers = get_pricing_tiers()
        self.assertEqual(
            [t.id for t in tiers],
            ['free', 'starter', 'plus', 'pro', 'team', 'business', 'enterprise'],
        )

        free, starter, plus, pro, team, business, enterprise = tiers
        self.assertTrue(free.is_free)
        self.assertEqual(free.price_monthly, 0)
        self.assertEqual(starter.price_monthly, 15)
        self.assertEqual(starter.price_annually, 12)
        self.assertEqual(plus.price_monthly, 35)
        self.assertEqual(plus.price_annually, 28)
        self.assertTrue(plus.featured)
        self.assertEqual(pro.price_monthly, 50)
        self.assertEqual(pro.price_annually, 40)

        self.assertEqual(team.price_monthly, 59)
        self.assertEqual(team.price_annually, 47)
        self.assertEqual([a.id for a in team.addons], ['team_request_block'])
        self.assertEqual(team.addons[0].price_monthly, 25)
        self.assertEqual(team.addons[0].unit_suffix, '/mo per 50 requests')

        self.assertEqual(business.price_monthly, 199)
        self.assertEqual(business.price_annually, 165)
        self.assertEqual([a.id for a in business.addons], ['doc_block'])
        self.assertEqual(business.addons[0].price_monthly, 45)
        self.assertEqual(business.addons[0].unit_suffix, '/mo per 100 requests')

        self.assertEqual(enterprise.price_monthly, 500)
        self.assertEqual(enterprise.price_annually, 415)
        self.assertEqual([a.id for a in enterprise.addons], ['enterprise_request_block'])
        self.assertEqual(enterprise.addons[0].price_monthly, 35)
        self.assertEqual(enterprise.addons[0].unit_suffix, '/mo per 250 requests')


@override_settings(BILLING_ENABLED=True, STRIPE_API_KEY='sk_test_fake')
class PricingStripeTests(TestCase):
    @patch('landing.pricing.stripe.Price.search')
    def test_stripe_prices_override_fallback(self, mock_search):
        mock_search.return_value = FakeSearchResult([
            fake_price(1500, 'month', 'price_starter_m', plan='regular'),
            fake_price(14400, 'year', 'price_starter_y', plan='regular'),
            fake_price(19900, 'month', 'price_biz_m', type='org_seat', tier='BUSINESS'),
            fake_price(4500, 'month', 'price_block_m', type='org_doc_block', tier='BUSINESS'),
        ])

        tiers = get_pricing_tiers()
        free, starter, plus, pro, team, business, enterprise = tiers

        # 'regular' is the existing live Stripe product metadata (see
        # PRODUCTION_INCIDENT.md) -- still matches Starter for backward compat.
        self.assertEqual(starter.price_monthly, 15)
        self.assertEqual(starter.price_annually, 12)
        self.assertEqual(starter.price_id_monthly, 'price_starter_m')
        self.assertEqual(starter.price_id_annually, 'price_starter_y')

        self.assertEqual(business.price_monthly, 199)
        self.assertEqual(business.price_id_monthly, 'price_biz_m')

        (doc_block,) = business.addons
        self.assertEqual(doc_block.price_monthly, 45)
        self.assertEqual(doc_block.price_id_monthly, 'price_block_m')

        # Not wired to Stripe yet -- always fallback values.
        self.assertEqual(plus.price_monthly, 35)
        self.assertIsNone(plus.price_id_monthly)
        self.assertEqual(pro.price_monthly, 50)
        self.assertIsNone(pro.price_id_monthly)
        self.assertEqual(team.price_monthly, 59)
        self.assertIsNone(team.price_id_monthly)
        self.assertEqual(enterprise.price_monthly, 500)
        self.assertIsNone(enterprise.price_id_monthly)

    @patch('landing.pricing.stripe.Price.search')
    def test_stripe_starter_metadata_convention_also_matches(self, mock_search):
        """Once/if the Stripe product metadata is renamed from 'regular' to
        'starter', it should still resolve to the Starter tier."""
        mock_search.return_value = FakeSearchResult([
            fake_price(1500, 'month', 'price_starter_m', plan='starter'),
        ])

        tiers = get_pricing_tiers()
        starter = tiers[1]
        self.assertEqual(starter.price_id_monthly, 'price_starter_m')

    @patch('landing.pricing.stripe.Price.search')
    def test_missing_addon_falls_back_independently(self, mock_search):
        """A missing org_doc_block match should only affect that one addon --
        not the base Business price."""
        mock_search.return_value = FakeSearchResult([
            fake_price(19900, 'month', 'price_biz_m', type='org_seat', tier='BUSINESS'),
        ])

        with self.assertLogs('landing.pricing', level='WARNING') as logs:
            tiers = get_pricing_tiers()

        business = tiers[5]
        self.assertEqual(business.price_id_monthly, 'price_biz_m')
        (doc_block,) = business.addons
        self.assertEqual(doc_block.price_monthly, 45)  # fallback placeholder
        self.assertIsNone(doc_block.price_id_monthly)
        self.assertTrue(any('doc_block' in message for message in logs.output))

    @patch('landing.pricing.stripe.Price.search')
    def test_stripe_search_exception_falls_back_entirely(self, mock_search):
        mock_search.side_effect = Exception('stripe is down')

        with self.assertLogs('landing.pricing', level='ERROR'):
            tiers = get_pricing_tiers()

        self.assertEqual(
            [t.id for t in tiers],
            ['free', 'starter', 'plus', 'pro', 'team', 'business', 'enterprise'],
        )
        self.assertEqual(tiers[5].price_monthly, 199)
        self.assertIsNone(tiers[1].price_id_monthly)


class PricingSSRTests(TestCase):
    def test_homepage_renders_all_tiers_and_dedicated_contact_line(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Individual tab: Starter/Plus/Pro replace the old single 'individual' card.
        self.assertIn('data-tier="starter"', content)
        self.assertIn('data-tier="plus"', content)
        self.assertIn('data-tier="pro"', content)
        self.assertIn('50 signature requests/mo', content)  # Plus
        self.assertIn('Up to 500 recipients per document', content)  # Pro

        # Organization tab: Team/Business/Enterprise Shared, matching the live ladder.
        self.assertIn('data-tier="team"', content)
        self.assertIn('data-tier="business"', content)
        self.assertIn('data-tier="enterprise"', content)
        self.assertIn('$199', content)
        self.assertIn('For growing organizations running business rules and workflows at scale.', content)  # Business description
        self.assertIn('150 signature requests/mo', content)  # Business feature
        self.assertIn('+$25/mo per 50 requests', content)  # Team's extra-requests addon

        # Free has no card -- the mockup doesn't show one -- but it's not deleted
        # from the data model (still a real, supported signup slug).
        self.assertNotIn('data-tier="free"', content)

        self.assertIn('Most popular', content)
        self.assertIn('Get started', content)

        # Individual/Organization + Monthly/Annual dual toggle.
        self.assertIn('data-family-group="individual"', content)
        self.assertIn('data-family-group="organization"', content)
        self.assertIn('id="planFamilyToggle"', content)
        self.assertIn('id="billingToggle"', content)

        # Enterprise Dedicated is sales-assisted only -- no card, just the contact line.
        self.assertIn('Need a dedicated instance, custom domain, or SSO?', content)
        self.assertIn('Talk to sales', content)


class PricingAnnualLabelTests(TestCase):
    """Switching to Annual used to change the number but leave the label
    reading "/ month" -- a visitor would see e.g. $47 and actually be charged
    twelve times that up front. Both the period text and the real once-a-year
    charge must be server-rendered so the toggle needs no network call, the
    same pattern .pricing-amount already uses."""

    def setUp(self):
        self.html = self.client.get('/').content.decode()

    def test_period_label_has_both_billing_variants(self):
        periods = re.findall(
            r'<span class="pricing-period"\s+data-monthly="([^"]*)"\s+data-annual="([^"]*)">',
            self.html,
        )
        # One per visible card (Free has no card): Starter, Plus, Pro, Team,
        # Business, Enterprise Shared.
        self.assertEqual(len(periods), 6)
        for monthly, annual in periods:
            self.assertEqual(monthly, '/ month')
            self.assertEqual(annual, '/ month, billed annually')

    def test_annual_total_charged_is_server_rendered_and_hidden_by_default(self):
        """Hidden (not just visually) so it isn't read out or found by a
        Monthly-mode reader search before Annual is selected."""
        notes = re.findall(r'<p class="pricing-annual-total" hidden>\$(\d+) billed yearly</p>', self.html)
        self.assertEqual(len(notes), 6)

    def test_annual_total_is_the_monthly_equivalent_times_twelve(self):
        for tier in get_pricing_tiers():
            if tier.is_free:
                continue
            self.assertIn(f'${tier.price_annually * 12} billed yearly', self.html)

    def test_price_annually_total_property_matches_the_advertised_figures(self):
        """Pins the worked examples from the annual-saving docstring/README --
        Team $564, Business $1,980, Enterprise Shared $4,980."""
        by_id = {t.id: t for t in _fallback_tiers()}
        self.assertEqual(by_id['team'].price_annually_total, 564)
        self.assertEqual(by_id['business'].price_annually_total, 1980)
        self.assertEqual(by_id['enterprise'].price_annually_total, 4980)


class PricingCapabilityTests(TestCase):
    """The page spends most of its length on Intake/Control/Records/Connect
    but previously no card said which plan actually includes them. Facts
    below come from packages/lib/constants/org-tiers.ts and nav-config.tsx in
    the app repo -- individual plans are e-signature only; Signature Inbox,
    business rules, approvals, workflows and Repositories are org-only."""

    def test_individual_tiers_say_e_signature_only(self):
        tiers = {t.id: t for t in get_pricing_tiers()}
        for tier_id in ('starter', 'plus', 'pro'):
            capability = ' '.join(tiers[tier_id].capabilities)
            self.assertIn('E-signature only', capability)
            self.assertIn('Repositories', capability)

    def test_team_has_inbox_and_rules_but_not_repositories_or_api(self):
        team = next(t for t in get_pricing_tiers() if t.id == 'team')
        capability = ' '.join(team.capabilities)
        self.assertIn('Signature Inbox', capability)
        self.assertIn('business rules', capability)
        self.assertIn('no Repositories, no API', capability)

    def test_business_includes_repositories(self):
        business = next(t for t in get_pricing_tiers() if t.id == 'business')
        self.assertIn('Repositories', ' '.join(business.capabilities))

    def test_enterprise_shared_is_positioned_as_everything_business_has(self):
        """Enterprise Shared's capability set is identical to Business's (both
        include Repositories) -- it differs only in allowances, so the line
        says "everything in Business" rather than re-listing Repositories."""
        enterprise = next(t for t in get_pricing_tiers() if t.id == 'enterprise')
        self.assertIn('Everything in Business', ' '.join(enterprise.capabilities))

    def test_capability_line_renders_once_per_visible_card(self):
        html = self.client.get('/').content.decode()
        self.assertEqual(html.count('class="pricing-capability"'), 6)

    def test_document_manager_has_been_renamed_to_repositories(self):
        """Business/Enterprise Shared features used to say 'Document Manager
        included' -- 'Repositories' is the app's actual user-facing name."""
        html = self.client.get('/').content.decode()
        self.assertIn('Repositories included', html)
        self.assertNotIn('Document Manager', html)


class PricingSignupSlugTests(TestCase):
    """The app's /signup?plan= only accepts free|individual|team|business|
    enterprise (LANDING_PLAN_PARAM_SPEC.md); anything else is silently
    ignored. Starter is the app's $15/mo "individual" plan under a different
    local id, so it must send that slug rather than this site's 'starter'."""

    def test_starter_maps_to_the_apps_individual_slug(self):
        starter = next(t for t in get_pricing_tiers() if t.id == 'starter')
        self.assertEqual(starter.signup_slug, 'individual')

    def test_team_business_enterprise_have_no_override_because_ids_already_match(self):
        tiers = {t.id: t for t in get_pricing_tiers()}
        for tier_id in ('team', 'business', 'enterprise'):
            self.assertIsNone(tiers[tier_id].signup_slug)

    def test_signup_links_use_the_resolved_slug(self):
        html = self.client.get('/').content.decode()
        self.assertIn('/signup?plan=individual"', html)
        self.assertNotIn('/signup?plan=starter"', html)
        # Plus/Pro have no app-side slug yet -- still send tier.id verbatim
        # until the app adds one (see the comments in landing/pricing.py).
        self.assertIn('/signup?plan=plus"', html)
        self.assertIn('/signup?plan=pro"', html)
        self.assertIn('/signup?plan=team"', html)
        self.assertIn('/signup?plan=business"', html)
        self.assertIn('/signup?plan=enterprise"', html)


class FinalCtaCopyTests(TestCase):
    """The closing CTA used to say 'talk to sales about Team, Business or
    Enterprise Shared' directly beside self-serve 'Get started' buttons on
    those same cards -- a direct contradiction of what the cards actually
    offer."""

    def test_cta_no_longer_contradicts_the_self_serve_org_cards(self):
        html = self.client.get('/').content.decode()
        self.assertIn('Start on any plan today', html)
        self.assertNotIn('Start on Starter, Plus or Pro today', html)
