"""
API Views for HubSign Landing Page

These endpoints support the sign-in modal functionality:
- Tenant/subdomain validation
- Magic link authentication
- User signup
"""

import re
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

# Simulated tenant database (replace with actual database/API call)
VALID_TENANTS = {
    'demo': {'name': 'Demo Company', 'active': True},
    'acme': {'name': 'Acme Inc', 'active': True},
    'test': {'name': 'Test Organization', 'active': True},
}


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring."""
    return Response({
        'status': 'healthy',
        'service': 'hubsign-landing'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_tenant(request):
    """
    Validate if a subdomain/tenant exists.
    
    Request body:
        {
            "subdomain": "acme"
        }
    
    Response:
        {
            "valid": true,
            "redirect_url": "https://acme.hubsign.io",
            "tenant_name": "Acme Inc"
        }
    """
    subdomain = request.data.get('subdomain', '').strip().lower()
    
    # Validate subdomain format
    if not subdomain:
        return Response({
            'valid': False,
            'message': 'Subdomain is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check subdomain format (alphanumeric and hyphens, no leading/trailing hyphens)
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', subdomain):
        return Response({
            'valid': False,
            'message': 'Invalid subdomain format'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if tenant exists (replace with actual database/API lookup)
    tenant = VALID_TENANTS.get(subdomain)
    
    if tenant and tenant.get('active'):
        # Determine protocol based on debug mode
        protocol = 'http' if settings.DEBUG else 'https'
        
        return Response({
            'valid': True,
            'redirect_url': f'{protocol}://{subdomain}.hubsign.io',
            'tenant_name': tenant.get('name')
        })
    
    return Response({
        'valid': False,
        'message': 'Organization not found. Please check your subdomain or contact your administrator.'
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_magic_link(request):
    """
    Send a passwordless magic link to the user's email.
    
    Request body:
        {
            "email": "user@example.com"
        }
    
    Response:
        {
            "success": true,
            "message": "Sign-in link sent"
        }
    """
    email = request.data.get('email', '').strip().lower()
    
    # Validate email format
    if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return Response({
            'success': False,
            'message': 'Valid email address is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Generate magic link token (in production, use proper token generation)
        # token = generate_magic_link_token(email)
        # magic_link = f"https://app.hubsign.io/auth/verify?token={token}"
        
        # For now, just log the attempt
        logger.info(f"Magic link requested for: {email}")
        
        # Send email (uses console backend in development)
        if not settings.DEBUG:
            send_mail(
                subject='Sign in to HubSign',
                message=f'Click here to sign in to HubSign: https://app.hubsign.io/auth/verify',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hubsign.io'),
                recipient_list=[email],
                fail_silently=False,
            )
        
        return Response({
            'success': True,
            'message': 'Sign-in link sent to your email'
        })
        
    except Exception as e:
        logger.error(f"Failed to send magic link: {e}")
        return Response({
            'success': False,
            'message': 'Failed to send sign-in link. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    Create a new user account.
    
    Request body:
        {
            "email": "user@company.com",
            "name": "John Doe",
            "company": "Acme Inc"
        }
    
    Response:
        {
            "success": true,
            "message": "Account created. Check your email to verify."
        }
    """
    email = request.data.get('email', '').strip().lower()
    name = request.data.get('name', '').strip()
    company = request.data.get('company', '').strip()
    
    # Validate required fields
    if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return Response({
            'success': False,
            'message': 'Valid email address is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not name:
        return Response({
            'success': False,
            'message': 'Name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # In production, create user in database and send verification email
        logger.info(f"Signup request: {email}, {name}, {company}")
        
        # Send welcome/verification email
        if not settings.DEBUG:
            send_mail(
                subject='Welcome to HubSign',
                message=f'Hi {name},\n\nThank you for signing up! Click here to verify your email: https://app.hubsign.io/auth/verify',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hubsign.io'),
                recipient_list=[email],
                fail_silently=False,
            )
        
        return Response({
            'success': True,
            'message': 'Account created successfully. Check your email to verify.'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Signup failed: {e}")
        return Response({
            'success': False,
            'message': 'Signup failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
