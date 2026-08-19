from unittest.mock import patch

from django.test import TestCase, override_settings

from .pricing import get_pricing_tiers


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
            [t.id for t in tiers], ['free', 'individual', 'team', 'business', 'enterprise'],
        )

        free, individual, team, business, enterprise = tiers
        self.assertTrue(free.is_free)
        self.assertEqual(free.price_monthly, 0)
        self.assertEqual(individual.price_monthly, 15)
        self.assertEqual(individual.price_annually, 12)

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
            fake_price(1500, 'month', 'price_ind_m', plan='regular'),
            fake_price(14400, 'year', 'price_ind_y', plan='regular'),
            fake_price(19900, 'month', 'price_biz_m', type='org_seat', tier='BUSINESS'),
            fake_price(4500, 'month', 'price_block_m', type='org_doc_block', tier='BUSINESS'),
        ])

        tiers = get_pricing_tiers()
        free, individual, team, business, enterprise = tiers

        self.assertEqual(individual.price_monthly, 15)
        self.assertEqual(individual.price_annually, 12)
        self.assertEqual(individual.price_id_monthly, 'price_ind_m')
        self.assertEqual(individual.price_id_annually, 'price_ind_y')

        self.assertEqual(business.price_monthly, 199)
        self.assertEqual(business.price_id_monthly, 'price_biz_m')

        (doc_block,) = business.addons
        self.assertEqual(doc_block.price_monthly, 45)
        self.assertEqual(doc_block.price_id_monthly, 'price_block_m')

        # Not wired to Stripe yet -- always fallback values.
        self.assertEqual(team.price_monthly, 59)
        self.assertIsNone(team.price_id_monthly)
        self.assertEqual(enterprise.price_monthly, 500)
        self.assertIsNone(enterprise.price_id_monthly)

    @patch('landing.pricing.stripe.Price.search')
    def test_missing_addon_falls_back_independently(self, mock_search):
        """A missing org_doc_block match should only affect that one addon --
        not the base Business price."""
        mock_search.return_value = FakeSearchResult([
            fake_price(19900, 'month', 'price_biz_m', type='org_seat', tier='BUSINESS'),
        ])

        with self.assertLogs('landing.pricing', level='WARNING') as logs:
            tiers = get_pricing_tiers()

        business = tiers[3]
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
            [t.id for t in tiers], ['free', 'individual', 'team', 'business', 'enterprise'],
        )
        self.assertEqual(tiers[3].price_monthly, 199)
        self.assertIsNone(tiers[1].price_id_monthly)


class PricingSSRTests(TestCase):
    def test_homepage_renders_all_tiers_and_dedicated_contact_line(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertIn('data-tier="free"', content)
        self.assertIn('data-tier="individual"', content)
        self.assertIn('data-tier="team"', content)
        self.assertIn('data-tier="business"', content)
        self.assertIn('data-tier="enterprise"', content)
        self.assertIn('$199', content)
        self.assertIn('150 signature requests/mo', content)
        self.assertIn('Unlimited users', content)
        self.assertIn('1,500 pages/mo Smart OCR', content)
        self.assertIn('Document Manager', content)
        self.assertIn('Popular', content)
        self.assertIn('Get started', content)

        # Enterprise is a full-width band, not a 5th grid card.
        self.assertIn('pricing-banner', content)

        # Enterprise Dedicated is sales-assisted only -- no card, just the contact line.
        self.assertIn('Need a dedicated instance, custom domain, or SSO?', content)
        self.assertIn('Talk to sales', content)
