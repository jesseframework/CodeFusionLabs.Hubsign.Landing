from django.test import TestCase


class PricingApiTests(TestCase):
    def test_pricing_endpoint_returns_five_tiers_with_addons(self):
        response = self.client.get('/api/pricing/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['currency'], 'USD')
        tiers = data['tiers']
        self.assertEqual(
            [t['id'] for t in tiers], ['free', 'individual', 'team', 'business', 'enterprise'],
        )

        business = next(t for t in tiers if t['id'] == 'business')
        self.assertEqual(business['price_monthly'], 199)
        self.assertEqual([a['id'] for a in business['addons']], ['doc_block'])
        self.assertEqual(business['addons'][0]['price_monthly'], 45)

    def test_api_and_ssr_agree_on_business_price(self):
        """Both IndexView and PricingInfoView now read from the same shared
        landing.pricing.get_pricing_tiers() -- this is the direct regression
        test for eliminating the drift documented in PRODUCTION_INCIDENT.md."""
        api_response = self.client.get('/api/pricing/')
        api_business = next(t for t in api_response.json()['tiers'] if t['id'] == 'business')

        ssr_response = self.client.get('/')
        self.assertContains(ssr_response, '${}'.format(api_business['price_monthly']))
