import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from landing.pricing import get_pricing_tiers, tiers_as_dicts

from .serializers import (
    ContactFormSerializer,
    NewsletterSerializer,
)

logger = logging.getLogger(__name__)


class ContactFormView(APIView):
    """Handle contact form submissions."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ContactFormSerializer,
        responses={
            200: OpenApiResponse(description="Message sent successfully"),
            400: OpenApiResponse(description="Invalid form data"),
        }
    )
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process contact form
        # TODO: Send email, create CRM lead, etc.
        logger.info(f"Contact form submission: {serializer.validated_data}")
        
        return Response({
            'success': True,
            'message': 'Thank you for contacting us! We\'ll get back to you soon.',
        })


class NewsletterSignupView(APIView):
    """Handle newsletter signups."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=NewsletterSerializer,
        responses={
            200: OpenApiResponse(description="Subscribed successfully"),
            400: OpenApiResponse(description="Invalid email"),
        }
    )
    def post(self, request):
        serializer = NewsletterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Add to newsletter list
        # TODO: Integrate with email marketing service
        logger.info(f"Newsletter signup: {email}")
        
        return Response({
            'success': True,
            'message': 'You\'re subscribed! Watch your inbox for updates.',
        })


class PricingInfoView(APIView):
    """Get current pricing information, sourced from Stripe when billing is enabled.

    Thin JSON adapter over landing.pricing.get_pricing_tiers() -- that module is
    the single source of truth for pricing, shared with the server-rendered
    landing page (landing.views.IndexView). See PRODUCTION_INCIDENT.md for why
    this used to be a second, independently-maintained copy.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: OpenApiResponse(description="Pricing data")}
    )
    def get(self, request):
        """Return pricing tiers as JSON, sourced from Stripe when billing is enabled."""
        return Response({'tiers': tiers_as_dicts(get_pricing_tiers()), 'currency': 'USD'})


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'hubsign-landing',
        })
