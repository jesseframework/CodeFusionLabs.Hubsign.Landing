import logging
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    TenantLookupSerializer,
    SignInRequestSerializer,
    VerifyMagicLinkSerializer,
    ContactFormSerializer,
    NewsletterSerializer,
)

logger = logging.getLogger(__name__)


class TenantLookupView(APIView):
    """
    Look up a tenant by domain to determine where to redirect for sign-in.
    
    This checks if a company has their own HubSign subdomain/instance
    or if they should use the shared instance.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=TenantLookupSerializer,
        responses={
            200: OpenApiResponse(description="Tenant found"),
            404: OpenApiResponse(description="Tenant not found - use shared instance"),
        }
    )
    def post(self, request):
        serializer = TenantLookupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        domain = serializer.validated_data['domain']
        
        # Check if this domain has a dedicated HubSign instance
        tenant_info = self._lookup_tenant(domain)
        
        if tenant_info:
            return Response({
                'found': True,
                'tenant_name': tenant_info.get('name'),
                'signin_url': tenant_info.get('signin_url'),
                'subdomain': tenant_info.get('subdomain'),
            })
        else:
            # No dedicated instance - offer shared instance
            return Response({
                'found': False,
                'message': 'No dedicated instance found for this domain.',
                'shared_instance_url': f"https://{settings.HUBSIGN_SHARED_INSTANCE}",
                'can_create_account': True,
            })
    
    def _lookup_tenant(self, domain):
        """
        Look up tenant in the HubSign API or database.
        
        In production, this would call the actual HubSign API.
        """
        # TODO: Implement actual tenant lookup
        # For now, return None to simulate no dedicated instance
        
        # Example of how to call external API:
        # try:
        #     response = requests.get(
        #         f"{settings.HUBSIGN_API_URL}/tenants/lookup",
        #         params={'domain': domain},
        #         headers={'Authorization': f'Bearer {settings.HUBSIGN_API_KEY}'},
        #         timeout=10
        #     )
        #     if response.status_code == 200:
        #         return response.json()
        # except requests.RequestException as e:
        #     logger.error(f"Tenant lookup failed: {e}")
        
        return None


class SignInRequestView(APIView):
    """
    Request a magic sign-in link.
    
    Sends a passwordless sign-in email to the user.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=SignInRequestSerializer,
        responses={
            200: OpenApiResponse(description="Sign-in link sent"),
            400: OpenApiResponse(description="Invalid request"),
        }
    )
    def post(self, request):
        serializer = SignInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        domain = serializer.validated_data['domain']
        use_shared = serializer.validated_data.get('use_shared_instance', False)
        
        # Determine the target instance
        if use_shared:
            target_url = f"https://{settings.HUBSIGN_SHARED_INSTANCE}"
        else:
            # Look up or use domain-specific instance
            target_url = f"https://{domain.split('.')[0]}.hubsign.io"
        
        # Send magic link request to HubSign API
        success = self._send_magic_link(email, target_url)
        
        if success:
            return Response({
                'success': True,
                'message': 'Sign-in link sent! Check your email.',
                'email': email,
            })
        else:
            return Response({
                'success': False,
                'message': 'Unable to send sign-in link. Please try again.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _send_magic_link(self, email, target_url):
        """
        Send magic link via HubSign API.
        
        In production, this calls the actual HubSign auth service.
        """
        # TODO: Implement actual magic link sending
        logger.info(f"Would send magic link to {email} for {target_url}")
        return True


class VerifyMagicLinkView(APIView):
    """Verify a magic sign-in link token."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=VerifyMagicLinkSerializer,
        responses={
            200: OpenApiResponse(description="Token valid - redirect info"),
            400: OpenApiResponse(description="Invalid or expired token"),
        }
    )
    def post(self, request):
        serializer = VerifyMagicLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        
        # Verify token with HubSign API
        # TODO: Implement actual token verification
        
        return Response({
            'valid': True,
            'redirect_url': f"https://{settings.HUBSIGN_SHARED_INSTANCE}/dashboard",
        })


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
    """Get current pricing information."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="Pricing data")}
    )
    def get(self, request):
        """Return pricing tiers as JSON for dynamic updates."""
        return Response({
            'tiers': [
                {
                    'id': 'personal',
                    'name': 'Personal',
                    'price_monthly': 0,
                    'price_annually': 0,
                    'features': ['Up to 3 docs/month', 'Unlimited recipients', 'No credit card'],
                },
                {
                    'id': 'individual',
                    'name': 'Individual',
                    'price_monthly': 15,
                    'price_annually': 12,
                    'features': ['Unlimited documents', 'API access', 'Email support'],
                },
                {
                    'id': 'business',
                    'name': 'Business',
                    'price_monthly': 60,
                    'price_annually': 50,
                    'features': ['+$8/user for more', 'API + Automation', 'Embedding'],
                },
                {
                    'id': 'enterprise',
                    'name': 'Enterprise',
                    'price_monthly': 200,
                    'price_annually': 180,
                    'features': ['Custom domain', 'Unlimited teams', 'SMTP + OAuth'],
                },
            ],
            'currency': 'USD',
        })


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'hubsign-landing',
        })
