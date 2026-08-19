import logging
from dataclasses import asdict, dataclass, field, replace

from django.conf import settings

import stripe

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PricingAddon:
    id: str
    name: str
    price_monthly: int
    price_annually: int
    unit_suffix: str
    price_id_monthly: str | None = None
    price_id_annually: str | None = None


@dataclass(frozen=True)
class PricingTier:
    id: str
    name: str
    description: str
    features: list[str]
    featured: bool
    cta: str
    price_monthly: int
    price_annually: int
    is_free: bool = False
    price_id_monthly: str | None = None
    price_id_annually: str | None = None
    addons: list[PricingAddon] = field(default_factory=list)


def get_pricing_tiers() -> list[PricingTier]:
    """Single source of truth for pricing tiers, used by both the SSR landing
    page (landing.views.IndexView) and the JSON API (api.views.PricingInfoView).

    See PRODUCTION_INCIDENT.md for why this used to be two independently
    hardcoded copies that drifted out of sync.
    """
    tiers = None
    if settings.BILLING_ENABLED and settings.STRIPE_API_KEY:
        tiers = _fetch_from_stripe()
    return tiers or _fallback_tiers()


def tiers_as_dicts(tiers: list[PricingTier]) -> list[dict]:
    return [asdict(t) for t in tiers]


def _fetch_from_stripe() -> list[PricingTier] | None:
    stripe.api_key = settings.STRIPE_API_KEY
    try:
        # Search API (not List) to match app-hubsign's exact query convention.
        # Unlike List, Search is index-backed and can lag ~30-60s after a
        # Price/Product is created or edited in the Stripe dashboard -- not an
        # issue in steady state, but worth knowing during initial setup/testing.
        result = stripe.Price.search(
            query="active:'true' type:'recurring'",
            expand=['data.product'],
            limit=100,
        )
    except Exception as exc:
        logger.error('[pricing] Stripe Price.search failed, using fallback for all tiers: %s', exc)
        return None

    candidates = []
    for price in result.data:
        d = price.to_dict()
        product = d.get('product')
        if isinstance(product, dict) and product.get('active'):
            candidates.append(d)

    def matches(**meta):
        return [
            p for p in candidates
            if all((p['product'].get('metadata') or {}).get(k) == v for k, v in meta.items())
        ]

    fallback = {t.id: t for t in _fallback_tiers()}

    individual = _apply_price(fallback['individual'], matches(plan='regular'), 'Individual')

    business = _apply_price(
        fallback['business'], matches(type='org_seat', tier='BUSINESS'), 'Business',
    )
    business = replace(business, addons=[
        _apply_addon(business.addons[0], matches(type='org_doc_block', tier='BUSINESS')),
    ])

    # TODO(pricing): Team and Enterprise (Shared) aren't wired to Stripe yet -- no
    # confirmed metadata.plan/metadata.type convention exists for them (unlike
    # personal/individual/business, which were confirmed the hard way -- see
    # PRODUCTION_INCIDENT.md). Always sourced from fallback until Stripe products
    # and metadata are set up for these two tiers.
    return [fallback['free'], individual, fallback['team'], business, fallback['enterprise']]


def _apply_price(tier: PricingTier, price_matches: list[dict], label: str) -> PricingTier:
    monthly, annually, pid_m, pid_a = _resolve_interval_prices(price_matches)
    if monthly is None:
        logger.warning(
            '[pricing] No Stripe Price found for %s; using fallback $%s/mo',
            label, tier.price_monthly,
        )
        return tier
    return replace(
        tier, price_monthly=monthly, price_annually=annually,
        price_id_monthly=pid_m, price_id_annually=pid_a,
    )


def _apply_addon(addon: PricingAddon, price_matches: list[dict]) -> PricingAddon:
    monthly, annually, pid_m, pid_a = _resolve_interval_prices(price_matches)
    if monthly is None:
        logger.warning(
            '[pricing] No Stripe Price found for add-on %s; using fallback $%s%s',
            addon.id, addon.price_monthly, addon.unit_suffix,
        )
        return addon
    return replace(
        addon, price_monthly=monthly, price_annually=annually,
        price_id_monthly=pid_m, price_id_annually=pid_a,
    )


def _resolve_interval_prices(price_matches: list[dict]):
    monthly = next((p for p in price_matches if p['recurring']['interval'] == 'month'), None)
    yearly = next((p for p in price_matches if p['recurring']['interval'] == 'year'), None)
    if monthly is None:
        return None, None, None, None
    price_monthly = monthly['unit_amount'] // 100
    price_annually = round(yearly['unit_amount'] / 100 / 12) if yearly else price_monthly
    return price_monthly, price_annually, monthly['id'], yearly['id'] if yearly else None


def _fallback_tiers() -> list[PricingTier]:
    """See HubSign-Pricing-Plan.md Section 2 ("Proposed full ladder", "Feature
    differentiation", "Pricing page layout") and Section 4 ("Annual billing") for
    where these figures and the card copy rules come from. DMS is included in
    Business, not sold as a per-seat addon -- that was a live-site bug this ladder
    fixes, not a simplification made here.

    Card copy follows the doc's "Pricing page layout" rules: allowances first,
    add-on rate last as a muted footnote; user counts shown on every tier; cards
    kept to 3-4 lines (Business's DMS/API+embedding facts live in the comparison
    table below the grid -- not yet built -- rather than on the card itself).
    Enterprise is the exception: it renders as a full-width band, not a card, so
    it has room to show DMS/API+embedding inline.
    """
    return [
        PricingTier(
            id='free', name='Free',
            description='For casual signers.',
            features=['1 user', '3 signature requests/mo', '30 pages/mo Smart OCR'],
            featured=False, cta='Get started',
            price_monthly=0, price_annually=0, is_free=True,
        ),
        PricingTier(
            id='individual', name='Individual',
            description='For one person signing regularly.',
            features=['1 user', '15 signature requests/mo', '150 pages/mo Smart OCR', 'API access'],
            featured=False, cta='Get started',
            price_monthly=15, price_annually=12,
        ),
        PricingTier(
            id='team', name='Team',
            description='For small teams that outgrew Individual.',
            features=['Up to 20 users', '50 signature requests/mo', '400 pages/mo Smart OCR'],
            featured=True, cta='Get started',
            price_monthly=59, price_annually=47,
            addons=[
                PricingAddon(
                    id='team_request_block', name='Extra requests',
                    price_monthly=25, price_annually=21, unit_suffix='/mo per 50 requests',
                ),
            ],
        ),
        PricingTier(
            id='business', name='Business',
            description='Shared workspace for growing teams.',
            features=['Unlimited users', '150 signature requests/mo', '1,500 pages/mo Smart OCR'],
            featured=False, cta='Get started',
            price_monthly=199, price_annually=165,
            addons=[
                PricingAddon(
                    id='doc_block', name='Extra requests',
                    price_monthly=45, price_annually=37, unit_suffix='/mo per 100 requests',
                ),
            ],
        ),
        PricingTier(
            id='enterprise', name='Enterprise',
            description='High-volume signing on shared infrastructure.',
            features=[
                'Unlimited users', '1,000 signature requests/mo', '10,000 pages/mo Smart OCR',
                'Document Manager included', 'API + embedding',
            ],
            featured=False, cta='Get started',
            price_monthly=500, price_annually=415,
            addons=[
                PricingAddon(
                    id='enterprise_request_block', name='Extra requests',
                    price_monthly=35, price_annually=29, unit_suffix='/mo per 250 requests',
                ),
            ],
        ),
    ]
