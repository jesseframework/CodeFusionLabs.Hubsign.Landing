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

    # 'regular' is the existing live Stripe product (confirmed the hard way --
    # see PRODUCTION_INCIDENT.md), which was priced at Starter's $15/mo. Also
    # accept 'starter' going forward once/if the product metadata is renamed.
    starter = _apply_price(fallback['starter'], matches(plan='starter') or matches(plan='regular'), 'Starter')
    plus = _apply_price(fallback['plus'], matches(plan='plus'), 'Plus')
    pro = _apply_price(fallback['pro'], matches(plan='pro'), 'Pro')

    business = _apply_price(
        fallback['business'], matches(type='org_seat', tier='BUSINESS'), 'Business',
    )
    business = replace(business, addons=[
        _apply_addon(business.addons[0], matches(type='org_doc_block', tier='BUSINESS')),
    ])

    # TODO(pricing): Team and Enterprise (Shared) aren't wired to Stripe yet -- no
    # confirmed metadata.plan/metadata.type convention exists for them (unlike
    # business, which was confirmed the hard way -- see PRODUCTION_INCIDENT.md).
    # Plus and Pro are new tiers with no Stripe products yet either. All four are
    # always sourced from fallback until Stripe products and metadata exist.
    return [
        fallback['free'], starter, plus, pro,
        fallback['team'], business, fallback['enterprise'],
    ]


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
    where the Team/Business/Enterprise figures and the card copy rules come from.
    DMS is included in Business, not sold as a per-seat addon -- that was a
    live-site bug this ladder fixes, not a simplification made here.

    Card copy follows the doc's "Pricing page layout" rules: allowances first,
    add-on rate last as a muted footnote; user counts shown on every tier; cards
    kept to 3-4 lines.

    Starter/Plus/Pro replace the old single 'individual' $15/mo tier (see the new
    HubSign Landing Page mockup) -- Starter keeps Individual's old figures
    exactly, Plus and Pro are new. Their annual prices aren't specified anywhere
    yet (the mockup only shows monthly): applied the same 20% "acquisition tier"
    discount HubSign-Pricing-Plan.md Section 4 already uses for Individual/Team.
    Placeholder until real Stripe annual prices exist for Plus/Pro.
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
            id='starter', name='Starter',
            description='For one person signing occasionally.',
            features=[
                '20 signature requests/mo', 'Up to 10 recipients per document',
                '1 direct signing link', 'Standard support',
            ],
            featured=False, cta='Get started',
            price_monthly=15, price_annually=12,
        ),
        PricingTier(
            id='plus', name='Plus',
            description='For one person signing regularly.',
            features=[
                '50 signature requests/mo', 'Up to 50 recipients per document',
                '5 direct signing links', 'Email support',
            ],
            featured=True, cta='Get started',
            price_monthly=35, price_annually=28,
        ),
        PricingTier(
            id='pro', name='Pro',
            description='For power users who sign at volume.',
            features=[
                '100 signature requests/mo', 'Up to 500 recipients per document',
                '20 direct signing links', 'Priority email support',
            ],
            featured=False, cta='Get started',
            price_monthly=50, price_annually=40,
        ),
        PricingTier(
            id='team', name='Team',
            description='For a small team centralizing signing, approvals and records in one place.',
            features=['Up to 20 users', '50 signature requests/mo', '400 pages/mo Smart OCR'],
            featured=False, cta='Get started',
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
            description='For growing organizations running business rules and workflows at scale.',
            features=[
                'Unlimited users', '150 signature requests/mo', '1,500 pages/mo Smart OCR',
                'Document Manager included', 'API + embedding',
            ],
            featured=True, cta='Get started',
            price_monthly=199, price_annually=165,
            addons=[
                PricingAddon(
                    id='doc_block', name='Extra requests',
                    price_monthly=45, price_annually=37, unit_suffix='/mo per 100 requests',
                ),
            ],
        ),
        PricingTier(
            id='enterprise', name='Enterprise Shared',
            description='For large organizations sharing infrastructure and records across departments.',
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
