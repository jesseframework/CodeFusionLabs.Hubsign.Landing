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
    addon_matches = {
        'doc_block': matches(type='org_doc_block', tier='BUSINESS'),
        'dms': matches(type='org_dms', tier='BUSINESS'),
    }
    business = replace(business, addons=[
        _apply_addon(addon, addon_matches[addon.id]) for addon in business.addons
    ])

    return [fallback['personal'], individual, business]


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
    return [
        PricingTier(
            id='personal', name='Personal',
            description='For casual signers. Free forever.',
            features=['Up to 3 docs/month', 'Unlimited recipients', 'No credit card'],
            featured=False, cta='Get Started',
            price_monthly=0, price_annually=0, is_free=True,
        ),
        PricingTier(
            id='individual', name='Individual',
            description='Unlimited signing for individuals.',
            features=['Unlimited documents', 'API access', 'Email support'],
            featured=True, cta='Get Started',
            price_monthly=15, price_annually=12,
        ),
        PricingTier(
            id='business', name='Business',
            description='Shared workspace for growing teams.',
            features=['Unlimited users', '150 docs/mo included', 'API + Automation', 'Embedding'],
            featured=False, cta='Get Started',
            # CONFIRMED $199/mo flat (not per-seat). No annual discount is documented
            # anywhere -- price_annually intentionally == price_monthly.
            # TODO(pricing): replace with real annual figures once Stripe test-mode
            # Prices exist.
            price_monthly=199, price_annually=199,
            addons=[
                PricingAddon(
                    id='doc_block', name='Extra docs',
                    # CONFIRMED $45/mo per +100 docs. TODO(pricing): annual unconfirmed.
                    price_monthly=45, price_annually=45, unit_suffix='/mo per +100 docs',
                ),
                PricingAddon(
                    id='dms', name='Document Manager',
                    # CONFIRMED $15/seat/mo. TODO(pricing): annual unconfirmed.
                    price_monthly=15, price_annually=15, unit_suffix='/seat/mo',
                ),
            ],
        ),
    ]
