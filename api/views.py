from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from landing.pricing import get_pricing_tiers, tiers_as_dicts


class PricingInfoView(APIView):
    """Get current pricing information, sourced from Stripe when billing is enabled.

    Thin JSON adapter over landing.pricing.get_pricing_tiers() -- that module is
    the single source of truth for pricing, shared with the server-rendered
    landing page (landing.views.IndexView). See PRODUCTION_INCIDENT.md for why
    this used to be a second, independently-maintained copy.

    The landing page no longer *depends* on this endpoint to render prices --
    both the monthly and annual figures are server-rendered into the markup so
    the billing toggle works with no network round-trip. See landing/views.py.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: OpenApiResponse(description="Pricing data")}
    )
    def get(self, request):
        """Return pricing tiers as JSON, sourced from Stripe when billing is enabled."""
        return Response({'tiers': tiers_as_dicts(get_pricing_tiers()), 'currency': 'USD'})


class HealthCheckView(APIView):
    """Health check endpoint for monitoring.

    Referenced by the Dockerfile HEALTHCHECK, docker-compose and nginx. The path
    is /api/health/ -- several configs used to point at a /api/v1/health/ that
    never existed.
    """
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiResponse(description="Service is healthy")})
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'hubsign-landing',
        })
